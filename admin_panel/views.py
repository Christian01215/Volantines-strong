import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import supabase
import os

# Supabase client initialization
supabase_url = os.environ.get("SUPABASE_URL") or ""
supabase_key = os.environ.get("SUPABASE_KEY") or ""
if supabase_url and supabase_key:
    sb = supabase.create_client(supabase_url, supabase_key)
else:
    sb = None


def require_supabase(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not sb:
            messages.error(request, "Configuración de Supabase no disponible.")
            return redirect("admin_panel:login")
        return view_func(request, *args, **kwargs)
    return wrapper


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("admin_email")
        password = request.POST.get("admin_password")
        # Simple hardcoded admin for demo - in production use Django auth
        if email == "admin@volantinesstrong.cl" and password == "admin123":
            request.session["admin_logged_in"] = True
            return redirect("admin_panel:dashboard")
        else:
            messages.error(request, "Credenciales incorrectas.")
    return render(request, "admin_panel/login.html")


@login_required
def logout_view(request):
    request.session.pop("admin_logged_in", None)
    return redirect("admin_panel:login")


@login_required
def dashboard(request):
    from .models import Order, Product
    orders = Order.objects.all().order_by("-" + "created_at")[:10]
    products = Product.objects.all()[:10]
    return render(request, "admin_panel/dashboard.html", {"orders": orders, "products": products})


# --- Product CRUD ---

@login_required
def product_list(request):
    from .models import Product
    products = Product.objects.all().order_by("-" + "created_at")
    return render(request, "admin_panel/product_list.html", {"products": products})


@login_required
@require_http_methods(["GET", "POST"])
def product_create(request):
    if request.method == "POST":
        name = request.POST.get("prod_name")
        category_id = request.POST.get("prod_category")
        price = request.POST.get("prod_price")
        stock = request.POST.get("prod_stock")
        specs = request.POST.get("prod_specs")
        image_file = request.FILES.get("prod_image_file")
        
        from products.models import Category
        category = get_object_or_404(Category, pk=category_id) if category_id else None
        
        product = Product.objects.create(
            name=name,
            category=category,
            price=int(price) if price else 0,
            stock=int(stock) if stock else 0,
            specs=specs,
        )
        
        # Upload image to Supabase Storage if available
        if image_file and sb:
            file_path = f"products/{product.pk}/{image_file.name}"
            try:
                sb.storage.from_("product-images").upload(file_path, image_file.read())
                # Store the path in the product model
                product.image = file_path
                product.save(update_fields=["image"])
            except Exception as e:
                messages.warning(request, f"Producto creado, pero error al subir imagen: {e}")
        elif image_file:
            # Save with FileSystemStorage
            path = default_storage.save(f"media/{image_file.name}", image_file)
            product.image = path
            product.save(update_fields=["image"])
        
        messages.success(request, f"Producto '{name}' creado exitosamente.")
        return redirect("admin_panel:product_list")
    
    from products.models import Category
    categories = Category.objects.all().order_by("name")
    return render(request, "admin_panel/product_form.html", {"categories": categories, "action": "Crear"})


@login_required
@require_http_methods(["GET", "POST"])
def product_edit(request, product_id):
    from products.models import Category
    product = get_object_or_404(Product, pk=product_id)
    categories = Category.objects.all().order_by("name")
    
    if request.method == "POST":
        name = request.POST.get("prod_name")
        category_id = request.POST.get("prod_category")
        price = request.POST.get("prod_price")
        stock = request.POST.get("prod_stock")
        specs = request.POST.get("prod_specs")
        image_file = request.FILES.get("prod_image_file")
        
        if name:
            product.name = name
        if category_id:
            product.category = get_object_or_404(Category, pk=category_id)
        if price:
            product.price = int(price)
        if stock:
            product.stock = int(stock)
        if specs:
            product.specs = specs
        
        # Upload new image if provided
        if image_file:
            if sb:
                file_path = f"products/{product.pk}/{image_file.name}"
                try:
                    sb.storage.from_("product-images").upload(file_path, image_file.read())
                    product.image = file_path
                except Exception as e:
                    messages.warning(request, f"Error al subir imagen: {e}")
            else:
                path = default_storage.save(f"media/{image_file.name}", image_file)
                product.image = path
        
        product.save(update_fields=["name", "category", "price", "stock", "specs", "image"])
        messages.success(request, f"Producto '{name}' actualizado exitosamente.")
        return redirect("admin_panel:product_list")
    
    return render(request, "admin_panel/product_form.html", {"product": product, "categories": categories, "action": "Editar"})


# --- Order management ---

@login_required
def order_list(request):
    from .models import Order
    orders = Order.objects.all().order_by("-" + "created_at")
    return render(request, "admin_panel/order_list.html", {"orders": orders})


@login_required
@require_http_methods(["GET", "POST"])
def order_status_update(request, order_code):
    from .models import Order
    order = get_object_or_404(Order, code=order_code)
    if request.method == "POST":
        new_status = request.POST.get("status")
        valid_choices = dict(Order.STATUS_CHOICES).keys()
        if new_status in valid_choices:
            order.status = new_status
            order.save(update_fields=["status"])
            messages.success(request, f"Estado actualizado a {order.get_status_display()}")
        else:
            messages.error(request, "Estado inválido.")
    return redirect("admin_panel:order_list")
