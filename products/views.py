from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from cart.models import CartItem
from cart.services import get_or_create_cart
from config.storage import StorageUploadError
from config.validators import MAX_DESIGN_SIZE, DESIGN_TYPES, validate_upload

from .models import Product, Category
from .services import upload_design


def catalog(request):
    categories = Category.objects.filter(is_active=True).order_by("order", "name")
    products = Product.objects.filter(is_active=True).select_related("category")
    query = request.GET.get("q")
    cat_filter = request.GET.get("category")
    if query:
        products = products.filter(name__icontains=query) | products.filter(specs__icontains=query)
    if cat_filter:
        products = products.filter(category__slug=cat_filter)
    return render(request, "storefront/index.html", {"categories": categories, "products": products, "query": query, "cat_filter": cat_filter})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    return render(request, "products/detail.html", {"product": product, "related": related})


def customize(request, slug):
    """RF-09: personalizador de carretes en HTML5 Canvas."""
    product = get_object_or_404(
        Product, slug=slug, is_active=True, category__slug="carretes"
    )
    return render(request, "products/customize.html", {"product": product})


@require_POST
def customize_upload(request, slug):
    """Recibe el PNG exportado, lo guarda y lo deja en el carrito como línea propia."""
    product = get_object_or_404(
        Product, slug=slug, is_active=True, category__slug="carretes"
    )
    design = request.FILES.get("design")
    if design is None:
        return JsonResponse({"ok": False, "message": "Falta la imagen del diseño."}, status=400)

    if product.stock <= 0:
        return JsonResponse({"ok": False, "message": f"{product.name} está agotado."}, status=400)

    invalid = validate_upload(design, DESIGN_TYPES, MAX_DESIGN_SIZE, "el diseño")
    if invalid:
        return JsonResponse({"ok": False, "message": invalid}, status=400)

    try:
        url, name, error = upload_design(design, product.slug)
    except StorageUploadError as exc:
        return JsonResponse({"ok": False, "message": str(exc)}, status=500)
    cart = get_or_create_cart(request)
    CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=1,
        price_at_time=product.price,
        design_url=url,
        design_name=name,
    )

    payload = {
        "ok": True,
        "design_url": url,
        "design_name": name,
        "redirect": reverse("cart:view"),
    }
    if error:
        payload["warning"] = f"El diseño se guardó localmente: {error}"
    return JsonResponse(payload)
