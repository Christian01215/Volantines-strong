from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
# products.Product - use string reference or import inside function

def view_cart(request):
    # Try to get or create cart from session
    cart_id = request.session.get("cart_id")
    if cart_id:
        cart = get_object_or_404(Cart, pk=cart_id)
        # Verify cart belongs to current session or create new
        if cart.session_key != request.session.session_key:
            cart = Cart.objects.create()
            request.session["cart_id"] = cart.pk
    else:
        cart = Cart.objects.create()
        request.session["cart_id"] = cart.pk
    
    items = cart.items.all()
    total = sum(item.line_total for item in items)
    return render(request, "cart/view.html", {"cart": cart, "items": items, "total": total})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart_id = request.session.get("cart_id")
    if cart_id:
        cart = Cart.objects.get(pk=cart_id)
    else:
        cart = Cart.objects.create()
        request.session["cart_id"] = cart.pk
    
    # Check if item already in cart
    existing = cart.items.filter(product=product).first()
    if existing:
        existing.quantity += 1
        existing.save()
    else:
        CartItem.objects.create(cart=cart, product=product, price_at_time=product.price)
    
    return redirect("cart:view")

def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart_id = request.session.get("cart_id")
    if cart_id:
        cart = Cart.objects.get(pk=cart_id)
        item = cart.items.filter(product=product).first()
        if item:
            item.delete()
    return redirect("cart:view")

def checkout(request):
    cart_id = request.session.get("cart_id")
    if not cart_id:
        return redirect("cart:view")
    cart = get_object_or_404(Cart, pk=cart_id)
    items = cart.items.all()
    if not items.exists():
        return redirect("cart:view")
    
    total = sum(item.line_total for item in items)
    return render(request, "cart/checkout.html", {"cart": cart, "items": items, "total": total})
