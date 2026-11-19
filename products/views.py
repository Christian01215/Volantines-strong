from django.shortcuts import render, get_object_or_404
from .models import Product, Category

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
