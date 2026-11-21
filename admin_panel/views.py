import mimetypes
from pathlib import Path

import supabase
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods, require_POST

from orders.models import Order
from products.models import Category, Product, ProductImage


def _upload_image(file, product_pk, gallery=False):
    """Sube imágenes al bucket de productos, con fallback al storage local."""
    content = file.read()
    filename = Path(file.name).name
    mimetype = file.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    suffix = "gallery" if gallery else "main"
    path = f"products/{product_pk}/{suffix}/{filename}"

    if settings.SUPABASE_URL and settings.SUPABASE_KEY and settings.SUPABASE_STORAGE_BUCKET:
        try:
            client = supabase.create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            bucket = client.storage.from_(settings.SUPABASE_STORAGE_BUCKET)
            bucket.upload(path, content, {"content-type": mimetype})
            return bucket.get_public_url(path)
        except Exception:
            pass

    local_path = default_storage.save(path, ContentFile(content))
    return default_storage.url(local_path)


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin_panel:dashboard")

    if request.method == "POST":
        email = request.POST.get("admin_email", "").strip()
        password = request.POST.get("admin_password", "")

        user = authenticate(request, username=email, password=password)
        if user is None:
            candidate = User.objects.filter(email__iexact=email).first()
            if candidate:
                user = authenticate(request, username=candidate.username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect("admin_panel:dashboard")

        messages.error(request, "Credenciales incorrectas o usuario sin acceso al panel.")

    return render(request, "admin_panel/login.html")


@require_POST
def logout_view(request):
    logout(request)
    return redirect("admin_panel:login")


@staff_member_required(login_url="admin_panel:login")
def dashboard(request):
    edit_id = request.GET.get("edit")
    editing_product = None
    if edit_id and edit_id.isdigit():
        editing_product = Product.objects.filter(pk=edit_id).first()

    return render(request, "admin_panel/dashboard.html", {
        "categories": Category.objects.all().order_by("order", "name"),
        "products": Product.objects.select_related("category").prefetch_related("gallery").all(),
        "orders": Order.objects.all().order_by("-created_at")[:20],
        "status_choices": Order.STATUS_CHOICES,
        "editing_product": editing_product,
    })


@staff_member_required(login_url="admin_panel:login")
def product_edit(request, product_id):
    return redirect(f"{reverse('admin_panel:dashboard')}?edit={product_id}")


@staff_member_required(login_url="admin_panel:login")
@require_http_methods(["GET", "POST"])
def product_save(request):
    if request.method != "POST":
        return redirect("admin_panel:dashboard")

    product_id = request.POST.get("prod_id")
    product = get_object_or_404(Product, pk=product_id) if product_id else Product()

    name = request.POST.get("prod_name", "").strip()
    if not name:
        messages.error(request, "El nombre del producto es obligatorio.")
        return redirect("admin_panel:dashboard")

    category_id = request.POST.get("prod_category", "").strip()
    category = Category.objects.filter(pk=category_id).first() if category_id.isdigit() else None
    if category is None and category_id:
        category, _ = Category.objects.get_or_create(
            name=category_id,
            defaults={"slug": slugify(category_id)},
        )
    if category is None:
        category = Category.objects.first()
    if category is None:
        category = Category.objects.create(name="General", slug="general")

    try:
        product.price = int(request.POST.get("prod_price") or 0)
        product.stock = int(request.POST.get("prod_stock") or 0)
    except ValueError:
        messages.error(request, "Precio y stock deben ser números.")
        return redirect("admin_panel:dashboard")

    product.name = name
    product.category = category
    product.specs = request.POST.get("prod_specs", "")
    product.description = request.POST.get("prod_desc", "")
    product.save()

    image_file = request.FILES.get("prod_image_file")
    if image_file:
        product.image = _upload_image(image_file, product.pk)
        product.save(update_fields=["image"])

    gallery_files = request.FILES.getlist("prod_gallery_files")[:4]
    if gallery_files:
        ProductImage.objects.filter(product=product).delete()
        for index, gallery_file in enumerate(gallery_files):
            ProductImage.objects.create(
                product=product,
                image=_upload_image(gallery_file, product.pk, gallery=True),
                order=index,
            )

    messages.success(request, f"Producto '{product.name}' guardado correctamente.")
    return redirect("admin_panel:dashboard")


@staff_member_required(login_url="admin_panel:login")
@require_POST
def product_delete(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    name = product.name
    product.delete()
    messages.success(request, f"Producto '{name}' eliminado.")
    return JsonResponse({"ok": True})


@staff_member_required(login_url="admin_panel:login")
@require_POST
def order_status_update(request, order_code):
    order = get_object_or_404(Order, code=order_code)
    new_status = request.POST.get("status")
    if new_status not in dict(Order.STATUS_CHOICES):
        return JsonResponse({"ok": False, "message": "Estado inválido"}, status=400)
    order.status = new_status
    order.save(update_fields=["status"])
    return JsonResponse({"ok": True, "status": order.get_status_display()})


@staff_member_required(login_url="admin_panel:login")
@require_POST
def order_notify(request, order_code):
    order = get_object_or_404(Order, code=order_code)
    if not order.customer_email:
        return JsonResponse({"ok": False, "message": "El pedido no tiene correo"}, status=400)

    send_mail(
        subject=f"Actualización de tu pedido {order.code} — Volantines Strong",
        message=(
            f"Hola {order.customer_name},\n\n"
            f"Tu pedido {order.code} está: {order.get_status_display()}.\n\n"
            "Gracias por comprar en Volantines Strong."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.customer_email],
        fail_silently=False,
    )
    return JsonResponse({"ok": True})


@staff_member_required(login_url="admin_panel:login")
@require_POST
def order_delete(request, order_code):
    order = get_object_or_404(Order, code=order_code)
    order.delete()
    return JsonResponse({"ok": True})
