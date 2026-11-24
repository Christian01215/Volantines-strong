import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from products.models import Product

from .services import (
    add_product,
    clear_cart,
    get_or_create_cart,
    remove_product,
    serialize_cart,
    set_quantity,
)


# ---------------------------------------------------------------------------
# Vistas HTML (carrito de página completa / sin JavaScript)
# ---------------------------------------------------------------------------

def view_cart(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related("product", "product__category")
    return render(request, "cart/view.html", {
        "cart": cart,
        "items": items,
        "total": cart.total,
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = get_or_create_cart(request)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 0:
        item = cart.items.filter(product=product).first()
        current = item.quantity if item else 0
        _, error = set_quantity(cart, product.pk, current + quantity)
    else:
        _, error = add_product(cart, product, quantity)

    if error:
        messages.error(request, error)
    else:
        messages.success(request, f"{product.name} actualizado en el carrito.")
    return redirect("cart:view")


@require_POST
def set_cart_quantity(request, product_id):
    cart = get_or_create_cart(request)
    _, error = set_quantity(cart, product_id, request.POST.get("quantity"))
    if error:
        messages.error(request, error)
    else:
        messages.success(request, "Cantidad actualizada en el carrito.")
    return redirect("cart:view")


def remove_from_cart(request, product_id):
    cart = get_or_create_cart(request)
    remove_product(cart, product_id)
    messages.info(request, "Producto eliminado del carrito.")
    return redirect("cart:view")


def checkout(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related("product", "product__category")
    if not items.exists():
        messages.info(request, "Tu carrito está vacío.")
        return redirect("cart:view")
    return render(request, "cart/checkout.html", {
        "cart": cart,
        "items": items,
        "total": cart.total,
    })


# ---------------------------------------------------------------------------
# API JSON usada por el drawer de la tienda
# ---------------------------------------------------------------------------

def _json_cart(cart, ok=True, message="", status=200, **extra):
    payload = {"ok": ok, **serialize_cart(cart)}
    if message:
        payload["message"] = message
    payload.update(extra)
    return JsonResponse(payload, status=status)


@require_GET
def cart_api(request):
    return _json_cart(get_or_create_cart(request))


@require_POST
def cart_api_add(request):
    cart = get_or_create_cart(request)
    product_id = request.POST.get("product_id") or request.POST.get("id")
    if not product_id:
        return _json_cart(cart, ok=False, message="Falta el producto", status=400)

    product = Product.objects.filter(pk=product_id, is_active=True).first()
    if product is None:
        return _json_cart(cart, ok=False, message="Producto no disponible", status=400)

    _, error = add_product(
        cart,
        product,
        request.POST.get("quantity", 1),
        request.POST.get("design_url", ""),
        request.POST.get("design_name", ""),
    )
    if error:
        return _json_cart(cart, ok=False, message=error, status=400)
    return _json_cart(cart, message=f"{product.name} agregado al carrito.")


@require_POST
def cart_api_update(request):
    cart = get_or_create_cart(request)
    item, error = set_quantity(cart, request.POST.get("product_id"), request.POST.get("quantity"))
    if error:
        return _json_cart(cart, ok=False, message=error, status=400)
    return _json_cart(cart)


@require_POST
def cart_api_remove(request):
    cart = get_or_create_cart(request)
    removed = remove_product(cart, request.POST.get("product_id"))
    if not removed:
        return _json_cart(cart, ok=False, message="El producto no está en el carrito", status=400)
    return _json_cart(cart)


@require_POST
def cart_api_clear(request):
    cart = get_or_create_cart(request)
    clear_cart(cart)
    return _json_cart(get_or_create_cart(request))
