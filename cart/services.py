"""Servicios del carrito persistido en base de datos.

Toda la tienda usa este carrito: ya no existe el carrito en localStorage.
Las vistas HTML y la API JSON comparten estas funciones para no duplicar reglas.
"""
from .models import Cart, CartItem


def get_or_create_cart(request):
    """Devuelve el carrito abierto de la sesión actual (lo crea si hace falta)."""
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    cart = Cart.objects.filter(session_key=session_key, completed=False).order_by("-pk").first()
    if cart is None:
        cart = Cart.objects.create(session_key=session_key)
    request.session["cart_id"] = cart.pk
    return cart


def serialize_cart(cart):
    """Representación JSON consumida por `static/js/cart.js`."""
    items = []
    for item in cart.items.select_related("product", "product__category"):
        product = item.product
        if product.image_url:
            image = product.image_url
        elif product.image:
            image = product.image.url
        else:
            image = ""
        items.append({
            "id": product.pk,
            "slug": product.slug,
            "name": product.name,
            "category": product.category.name,
            "price": item.price_at_time,
            "image": image,
            "quantity": item.quantity,
            "line_total": item.line_total,
            "stock": product.stock,
            "design_url": item.design_url,
            "design_name": item.design_name,
        })

    return {
        "items": items,
        "count": sum(item["quantity"] for item in items),
        "total": sum(item["line_total"] for item in items),
    }


def add_product(cart, product, quantity=1, design_url="", design_name=""):
    """Agrega (o suma) un producto. Devuelve (item, error)."""
    if product.stock <= 0:
        return None, f"{product.name} está agotado"

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(1, quantity)

    item = cart.items.filter(product=product).first()
    requested = quantity + (item.quantity if item else 0)
    if requested > product.stock:
        return None, f"Solo quedan {product.stock} unidades de {product.name}"

    if item:
        item.quantity = requested
        if design_url:
            item.design_url = design_url
            item.design_name = design_name
        item.save(update_fields=["quantity", "design_url", "design_name"])
    else:
        item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity,
            price_at_time=product.price,
            design_url=design_url,
            design_name=design_name,
        )
    return item, None


def set_quantity(cart, product_id, quantity):
    """Ajusta la cantidad de una línea. Devuelve (item, error)."""
    item = cart.items.filter(product_id=product_id).first()
    if item is None:
        return None, "El producto no está en el carrito"

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return None, "Cantidad inválida"

    if quantity <= 0:
        item.delete()
        return None, None

    if quantity > item.product.stock:
        return None, f"Solo quedan {item.product.stock} unidades de {item.product.name}"

    item.quantity = quantity
    item.save(update_fields=["quantity"])
    return item, None


def remove_product(cart, product_id):
    deleted, _ = cart.items.filter(product_id=product_id).delete()
    return deleted > 0


def clear_cart(cart):
    cart.items.all().delete()
    cart.completed = True
    cart.save(update_fields=["completed"])
