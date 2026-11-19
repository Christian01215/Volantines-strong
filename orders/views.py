from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from cart.models import Cart
from products.models import Product


def generate_order_from_cart(request):
    cart_id = request.session.get("cart_id")
    if not cart_id:
        messages.error(request, "No hay carrito activo.")
        return redirect("cart:view")
    
    cart = get_object_or_404(Cart, pk=cart_id)
    items = cart.items.all()
    if not items.exists():
        messages.error(request, "El carrito está vacío.")
        return redirect("cart:view")
    
    total = sum(item.line_total for item in items)
    
    import random
    import string
    code = "VC" + "".join(random.choices(string.digits, k=8))
    while Order.objects.filter(code=code).exists():
        code = "VC" + "".join(random.choices(string.digits, k=8))
    
    order = Order.objects.create(
        code=code,
        total=total,
        delivery_type="click_collect",
    )
    
    for cart_item in items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.price,
        )
    
    cart.delete()
    request.session.pop("cart_id", None)
    
    request.session["last_order_code"] = order.code
    
    return render(request, "orders/generated.html", {"order": order})


@login_required
def admin_order_list(request):
    from .models import Order
    status_filter = request.GET.get("status")
    if status_filter:
        orders = Order.objects.filter(status=status_filter).order_by("-" + "created_at")
    else:
        orders = Order.objects.all().order_by("-" + "created_at")
    return render(request, "orders/admin_list.html", {"orders": orders, "status_filter": status_filter})


@login_required
def admin_order_update(request, order_code):
    order = get_object_or_404(Order, code=order_code)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Order.STATUS_CHOICES).keys():
            order.status = new_status
            order.save(update_fields=["status"])
            messages.success(request, f"Estado actualizado a {order.get_status_display()}")
        else:
            messages.error(request, "Estado inválido.")
    return redirect("orders:admin_list")
