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
from django.db.models import Count, F, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods, require_POST

from config.validators import IMAGE_TYPES, MAX_IMAGE_SIZE, validate_upload
from orders.models import Order, OrderItem
from orders.services import send_customer_status_notification
from products.models import Category, Product, ProductImage


def _unique_product_slug(name, exclude_pk=None):
    """Genera un slug único para no violar el constraint UNIQUE de Product."""
    base = slugify(name) or "producto"
    slug = base
    counter = 2
    while True:
        queryset = Product.objects.filter(slug=slug)
        if exclude_pk:
            queryset = queryset.exclude(pk=exclude_pk)
        if not queryset.exists():
            return slug
        slug = f"{base}-{counter}"
        counter += 1


def _upload_image(file, product_pk, gallery=False):
    """Sube al bucket de productos.

    Devuelve ``(url_remota, ruta_local, error)``. Nunca guarda una URL dentro
    de un ImageField: eso provocaba rutas tipo /media/media/products/...
    """
    content = file.read()
    filename = Path(file.name).name
    mimetype = file.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    suffix = "gallery" if gallery else "main"
    path = f"products/{product_pk}/{suffix}/{filename}"
    error = None

    if settings.SUPABASE_URL and settings.SUPABASE_KEY and settings.SUPABASE_STORAGE_BUCKET:
        try:
            client = supabase.create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            bucket = client.storage.from_(settings.SUPABASE_STORAGE_BUCKET)
            bucket.upload(path, content, {"content-type": mimetype})
            return bucket.get_public_url(path), None, None
        except Exception as exc:
            error = str(exc)

    local_path = default_storage.save(path, ContentFile(content))
    return None, local_path, error


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin_panel:dashboard")

    if request.method == "POST":
        attempts = request.session.get("login_attempts", 0)
        if attempts >= 5:
            messages.error(request, "Demasiados intentos fallidos. Intenta nuevamente más tarde.")
            return render(request, "admin_panel/login.html")

        identifier = request.POST.get("admin_identifier", "").strip()
        password = request.POST.get("admin_password", "")

        user = authenticate(request, username=identifier, password=password)
        if user is None and identifier:
            # Puede haber varios usuarios con el mismo correo: probamos cada uno.
            for candidate in User.objects.filter(email__iexact=identifier):
                user = authenticate(request, username=candidate.username, password=password)
                if user is not None:
                    break

        if user is not None and user.is_staff:
            login(request, user)
            request.session.pop("login_attempts", None)
            return redirect("admin_panel:dashboard")

        request.session["login_attempts"] = attempts + 1
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

    orders = Order.objects.all().order_by("-created_at")
    date_from = (request.GET.get("date_from") or "").strip()
    date_to = (request.GET.get("date_to") or "").strip()
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)

    status_counts = [
        {"label": label, "value": orders.filter(status=value).count()}
        for value, label in Order.STATUS_CHOICES
    ]

    category_sales = list(
        OrderItem.objects.filter(order_id__in=orders.values("pk"))
        .values("product__category__name")
        .annotate(
            units=Sum("quantity"),
            revenue=Sum(F("price") * F("quantity")),
        )
        .order_by("-revenue")
    )
    for row in category_sales:
        row["name"] = row.pop("product__category__name")

    upcoming_pickups = (
        Order.objects.filter(pickup_date__gte=timezone.localdate())
        .exclude(status__in=["retirado", "cancelado"])
        .order_by("pickup_date", "pickup_slot")[:10]
    )

    return render(request, "admin_panel/dashboard.html", {
        "categories": Category.objects.all().order_by("order", "name"),
        "products": Product.objects.select_related("category").prefetch_related("gallery").all(),
        "orders": orders[:20],
        "status_choices": Order.STATUS_CHOICES,
        "editing_product": editing_product,
        "status_counts": status_counts,
        "category_sales": category_sales,
        "upcoming_pickups": upcoming_pickups,
        "date_from": date_from,
        "date_to": date_to,
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
    if not product.slug:
        product.slug = _unique_product_slug(name)
    product.category = category
    product.specs = request.POST.get("prod_specs", "")
    product.description = request.POST.get("prod_desc", "")
    product.save()

    image_file = request.FILES.get("prod_image_file")
    if image_file:
        invalid = validate_upload(image_file, IMAGE_TYPES, MAX_IMAGE_SIZE, "la imagen principal")
        if invalid:
            messages.error(request, invalid)
            return redirect("admin_panel:dashboard")
        remote_url, local_path, error = _upload_image(image_file, product.pk)
        product.image_url = remote_url or ""
        product.image = local_path or None
        product.save(update_fields=["image", "image_url"])
        if error:
            messages.warning(
                request,
                f"No se pudo subir la imagen al bucket '{settings.SUPABASE_STORAGE_BUCKET}': {error}. "
                "Se guardó en almacenamiento local.",
            )

    gallery_files = request.FILES.getlist("prod_gallery_files")[:4]
    if gallery_files:
        ProductImage.objects.filter(product=product).delete()
        for index, gallery_file in enumerate(gallery_files):
            invalid = validate_upload(gallery_file, IMAGE_TYPES, MAX_IMAGE_SIZE, "una imagen de galería")
            if invalid:
                messages.error(request, invalid)
                continue
            remote_url, local_path, error = _upload_image(gallery_file, product.pk, gallery=True)
            ProductImage.objects.create(
                product=product,
                image=local_path or None,
                image_url=remote_url or "",
                order=index,
            )
            if error:
                messages.warning(
                    request,
                    f"Una imagen de galería no se subió a Supabase: {error}. Se guardó localmente.",
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

    previous_status = order.status
    order.status = new_status
    order.save(update_fields=["status"])

    notification = ""
    if new_status == "listo_para_retiro" and previous_status != new_status:
        try:
            send_customer_status_notification(order)
        except Exception as exc:
            notification = f"El estado se actualizó, pero el correo no pudo enviarse: {exc}"

    payload = {"ok": True, "status": order.get_status_display()}
    if notification:
        payload["warning"] = notification
    return JsonResponse(payload)


@staff_member_required(login_url="admin_panel:login")
@require_POST
def order_notify(request, order_code):
    order = get_object_or_404(Order, code=order_code)
    if not order.customer_email:
        return JsonResponse({"ok": False, "message": "El pedido no tiene correo"}, status=400)

    try:
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
    except Exception as exc:
        return JsonResponse(
            {"ok": False, "message": f"No se pudo enviar el correo: {exc}"},
            status=500,
        )
    return JsonResponse({"ok": True})


@staff_member_required(login_url="admin_panel:login")
@require_POST
def order_delete(request, order_code):
    order = get_object_or_404(Order, code=order_code)
    order.delete()
    return JsonResponse({"ok": True})
