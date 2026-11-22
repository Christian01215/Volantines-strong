import logging
import random
import string

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from cart.services import clear_cart, get_or_create_cart
from config.validators import (
    MAX_RECEIPT_SIZE,
    RECEIPT_TYPES,
    validate_customer_data,
    validate_upload,
)
from products.models import Product

from .models import Order, OrderItem
from .services import (
    send_customer_confirmation,
    send_owner_notification,
    upload_receipt,
)

logger = logging.getLogger(__name__)


def _new_order_code():
    while True:
        code = "VC" + "".join(random.choices(string.digits, k=8))
        if not Order.objects.filter(code=code).exists():
            return code


def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def _error(request, message, status=400, redirect_to="cart:checkout"):
    if _is_ajax(request):
        return JsonResponse({"ok": False, "message": message}, status=status)
    messages.error(request, message)
    return redirect(redirect_to)


def generate_order_from_cart(request):
    """Compatibilidad: el checkout real ahora es checkout_submit."""
    messages.info(request, "Completa el formulario de checkout para registrar tu pedido.")
    return redirect("products:catalog")


@transaction.atomic
def _create_order_from_cart(request, cart):
    """Crea la orden a partir del carrito del servidor. Debe llamarse dentro de atomic().

    El carrito (y por lo tanto la sesión) se crea fuera de esta transacción:
    si hay rollback, la sesión del comprador no debe desaparecer.
    """
    cart_items = list(cart.items.select_related("product"))
    if not cart_items:
        raise ValueError("El carrito está vacío")

    product_ids = [item.product_id for item in cart_items]
    locked = {
        product.pk: product
        for product in Product.objects.select_for_update().filter(pk__in=product_ids)
    }

    validated = []
    for item in cart_items:
        product = locked.get(item.product_id)
        if product is None or not product.is_active:
            raise ValueError("Un producto ya no está disponible")
        if product.stock <= 0:
            raise ValueError(f"{product.name} está agotado")
        if item.quantity > product.stock:
            raise ValueError(
                f"Solo quedan {product.stock} unidades de {product.name}. "
                "Ajusta la cantidad en el carrito."
            )
        validated.append((item, product))

    total = sum(product.price * item.quantity for item, product in validated)

    order = Order.objects.create(
        code=_new_order_code(),
        customer_name=request.POST.get("customer_name", "").strip(),
        customer_rut=request.POST.get("customer_rut", "").strip(),
        customer_phone=request.POST.get("customer_phone", "").strip(),
        customer_email=request.POST.get("customer_email", "").strip(),
        delivery_type="click_collect",
        pickup_date=request.POST.get("pickup_date") or None,
        pickup_slot=request.POST.get("pickup_slot", ""),
        payment_method="transferencia",
        total=total,
        status="pendiente",
        cart=cart,
    )

    for item, product in validated:
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item.quantity,
            price=product.price,
            design_url=item.design_url,
            design_name=item.design_name,
        )
        product.stock -= item.quantity
        product.save(update_fields=["stock"])

    clear_cart(cart)
    return order


def checkout_submit(request):
    """Checkout real: valida carrito en servidor, descuenta stock y avisa al dueño."""
    if request.method != "POST":
        return JsonResponse({"ok": False, "message": "Método no permitido"}, status=405)

    required = ["customer_name", "customer_rut", "customer_phone", "customer_email"]
    missing = [field for field in required if not request.POST.get(field, "").strip()]
    if not request.FILES.get("receipt"):
        missing.append("receipt")
    if missing:
        return _error(request, "Faltan datos obligatorios: " + ", ".join(missing))

    errors = validate_customer_data(request.POST)
    errors.append(
        validate_upload(request.FILES["receipt"], RECEIPT_TYPES, MAX_RECEIPT_SIZE, "el comprobante")
        or ""
    )
    errors = [error for error in errors if error]
    if errors:
        return _error(request, " ".join(errors))

    cart = get_or_create_cart(request)
    try:
        order = _create_order_from_cart(request, cart)
    except ValueError as exc:
        return _error(request, str(exc))

    receipt_url, receipt_name, receipt_content, receipt_mimetype = upload_receipt(
        request.FILES["receipt"], order.code
    )
    order.receipt_url = receipt_url
    order.receipt_name = receipt_name
    order.save(update_fields=["receipt_url", "receipt_name"])

    email_sent = True
    try:
        send_owner_notification(
            order, receipt_url, receipt_name, receipt_content, receipt_mimetype
        )
    except Exception as exc:
        email_sent = False
        logger.exception("No se pudo enviar el aviso de la orden %s: %s", order.code, exc)

    customer_email_sent = False
    try:
        customer_email_sent = send_customer_confirmation(order)
    except Exception as exc:
        logger.exception("No se pudo confirmar la orden %s al cliente: %s", order.code, exc)

    message = (
        f"Pedido {order.code} registrado. Revisaremos tu comprobante."
        if email_sent
        else f"Pedido {order.code} registrado, pero el aviso por correo no pudo enviarse."
    )

    if not _is_ajax(request):
        return redirect("orders:success", code=order.code)

    return JsonResponse({
        "ok": True,
        "code": order.code,
        "email_sent": email_sent,
        "customer_email_sent": customer_email_sent,
        "message": message,
        "redirect": reverse("orders:success", kwargs={"code": order.code}),
    })


def checkout_success(request, code):
    order = get_object_or_404(Order, code=code)
    return render(request, "orders/success.html", {"order": order})


def order_track(request):
    """Consulta pública de estado por código de seguimiento."""
    code = (request.GET.get("code") or "").strip().upper()
    order = None
    error = ""
    if code:
        order = Order.objects.filter(code=code).first()
        if order is None:
            error = "No encontramos un pedido con ese código. Revisa los caracteres e intenta nuevamente."
    return render(
        request,
        "orders/track.html",
        {"order": order, "code": code, "error": error},
    )


def order_track_detail(request, code):
    order = get_object_or_404(Order, code=code)
    return render(request, "orders/track.html", {"order": order, "code": code})


@login_required
def admin_order_list(request):
    status_filter = request.GET.get("status")
    orders = Order.objects.prefetch_related("items").all()
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(
        request,
        "orders/admin_list.html",
        {"orders": orders, "status_filter": status_filter},
    )


@login_required
def admin_order_update(request, order_code):
    order = get_object_or_404(Order, code=order_code)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save(update_fields=["status"])
            messages.success(request, f"Estado actualizado a {order.get_status_display()}")
        else:
            messages.error(request, "Estado inválido.")
    return redirect("orders:admin_list")
