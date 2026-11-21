import json
import logging
import random
import string

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product

from .models import Order, OrderItem
from .services import send_owner_notification, upload_receipt

logger = logging.getLogger(__name__)


def _new_order_code():
    while True:
        code = "VC" + "".join(random.choices(string.digits, k=8))
        if not Order.objects.filter(code=code).exists():
            return code


def generate_order_from_cart(request):
    """Compatibilidad: el checkout real ahora es checkout_submit."""
    messages.info(request, "Completa el formulario de checkout para registrar tu pedido.")
    return redirect("products:catalog")


def checkout_submit(request):
    """Crea la orden desde el carrito del navegador y avisa por correo al dueño."""
    if request.method != "POST":
        return JsonResponse({"ok": False, "message": "Método no permitido"}, status=405)

    required = ["customer_name", "customer_rut", "customer_phone", "customer_email", "receipt"]
    missing = [field for field in required if not request.POST.get(field) and field != "receipt"]
    if not request.FILES.get("receipt"):
        missing.append("receipt")
    if missing:
        return JsonResponse(
            {"ok": False, "message": "Faltan datos obligatorios: " + ", ".join(missing)},
            status=400,
        )

    try:
        cart_items = json.loads(request.POST.get("cart_json", "[]"))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "message": "Carrito inválido"}, status=400)

    if not isinstance(cart_items, list) or not cart_items:
        return JsonResponse({"ok": False, "message": "El carrito está vacío"}, status=400)

    validated = []
    for entry in cart_items:
        try:
            product_id = entry.get("id") or entry.get("product_id")
            quantity = int(entry.get("quantity", 1))
        except (AttributeError, TypeError, ValueError):
            return JsonResponse({"ok": False, "message": "Carrito inválido"}, status=400)

        product = Product.objects.filter(pk=product_id, is_active=True).first()
        if product is None:
            return JsonResponse({"ok": False, "message": "Un producto ya no está disponible"}, status=400)
        if product.stock <= 0:
            return JsonResponse({"ok": False, "message": f"{product.name} está agotado"}, status=400)

        quantity = min(quantity, product.stock)
        validated.append((product, quantity))

    total = sum(product.price * quantity for product, quantity in validated)
    order = Order.objects.create(
        code=_new_order_code(),
        customer_name=request.POST.get("customer_name", "").strip(),
        customer_rut=request.POST.get("customer_rut", "").strip(),
        customer_phone=request.POST.get("customer_phone", "").strip(),
        customer_email=request.POST.get("customer_email", "").strip(),
        delivery_type=request.POST.get("delivery_type", "click_collect"),
        pickup_date=request.POST.get("pickup_date") or None,
        pickup_slot=request.POST.get("pickup_slot", ""),
        payment_method=request.POST.get("payment_method", ""),
        delivery_region=request.POST.get("delivery_region", ""),
        delivery_commune=request.POST.get("delivery_commune", ""),
        delivery_address=request.POST.get("delivery_address", ""),
        total=total,
        status="pendiente",
    )

    for product, quantity in validated:
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price,
        )

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

    response_message = (
        f"Pedido {order.code} registrado. Revisaremos tu comprobante."
        if email_sent
        else f"Pedido {order.code} registrado, pero el aviso por correo no pudo enviarse."
    )
    return JsonResponse({
        "ok": True,
        "code": order.code,
        "email_sent": email_sent,
        "message": response_message,
    })


@login_required
def admin_order_list(request):
    status_filter = request.GET.get("status")
    orders = Order.objects.all()
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
