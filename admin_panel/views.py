import logging
import mimetypes
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import F, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods, require_POST

from config.storage import save_upload
from config.validators import IMAGE_TYPES, MAX_IMAGE_SIZE, validate_upload
from orders.models import Order, OrderItem
from orders.services import (
    notify_customer,
    send_owner_notification,
    update_order_status,
)
from products.models import Category, Product, ProductImage

from .reports import build_orders_workbook, monthly_summary

logger = logging.getLogger(__name__)


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
    """Sube la imagen al bucket de productos.

    Devuelve ``(url_remota, ruta_local, error)``. Nunca guarda una URL dentro
    de un ImageField: eso provocaba rutas tipo /media/media/products/...
    En producción un fallo de Storage lanza StorageUploadError y la vista lo
    transforma en un mensaje, en vez de devolver un 500.
    """
    content = file.read()
    filename = Path(file.name).name
    mimetype = file.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    suffix = "gallery" if gallery else "main"
    path = f"products/{product_pk}/{suffix}/{filename}"

    result = save_upload(
        content,
        path,
        mimetype,
        settings.SUPABASE_STORAGE_BUCKET,
        f"la imagen {suffix} de {filename}",
    )
    return result.url, result.local_path, result.error


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
        "monthly_summary": monthly_summary(orders),
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
        product.cost = int(request.POST.get("prod_cost") or 0)
        product.stock = int(request.POST.get("prod_stock") or 0)
    except ValueError:
        messages.error(request, "Precio, costo y stock deben ser números.")
        return redirect("admin_panel:dashboard")

    product.name = name
    if not product.slug:
        product.slug = _unique_product_slug(name)
    product.category = category
    product.specs = request.POST.get("prod_specs", "")
    product.description = request.POST.get("prod_desc", "")
    product.save()

    try:
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
        invalid_gallery = [
            validate_upload(gallery_file, IMAGE_TYPES, MAX_IMAGE_SIZE, "una imagen de galería")
            for gallery_file in gallery_files
        ]
        invalid_gallery = [error for error in invalid_gallery if error]
        if invalid_gallery:
            messages.error(request, " ".join(invalid_gallery))
            return redirect("admin_panel:dashboard")

        if gallery_files:
            ProductImage.objects.filter(product=product).delete()
            for index, gallery_file in enumerate(gallery_files):
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
    except Exception as exc:
        logger.exception("No se pudieron guardar las imágenes del producto %s: %s", product.pk, exc)
        messages.error(
            request,
            f"El producto se guardó, pero las imágenes no pudieron subirse: {exc}",
        )
        return redirect("admin_panel:dashboard")

    messages.success(request, f"Producto '{product.name}' guardado correctamente.")
    return redirect("admin_panel:dashboard")


@staff_member_required(login_url="admin_panel:login")
@require_POST
def product_delete(request, product_id):
    """Baja lógica: oculta el producto sin destruir el historial de pedidos."""
    product = get_object_or_404(Product, pk=product_id)
    product.is_active = False
    product.save(update_fields=["is_active"])
    messages.success(request, f"Producto '{product.name}' desactivado.")
    return JsonResponse({
        "ok": True,
        "message": "Producto desactivado. Puedes reactivarlo cuando quieras.",
        "active": False,
    })


@staff_member_required(login_url="admin_panel:login")
@require_POST
def product_restore(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.is_active = True
    product.save(update_fields=["is_active"])
    messages.success(request, f"Producto '{product.name}' reactivado.")
    return JsonResponse({
        "ok": True,
        "message": "Producto reactivado.",
        "active": True,
    })


@staff_member_required(login_url="admin_panel:login")
@require_POST
def product_purge(request, product_id):
    """Elimina definitivamente un producto sólo si no está en el historial."""
    product = get_object_or_404(Product, pk=product_id)
    usages = OrderItem.objects.filter(product=product).count()
    if usages:
        return JsonResponse({
            "ok": False,
            "message": (
                f"No se puede eliminar: este producto aparece en {usages} pedido(s). "
                "Usá 'Desactivar' para ocultarlo sin borrar el historial."
            ),
        }, status=400)

    name = product.name
    product.delete()
    messages.success(request, f"Producto '{name}' eliminado definitivamente.")
    return JsonResponse({
        "ok": True,
        "message": f"Producto '{name}' eliminado definitivamente.",
    })


@staff_member_required(login_url="admin_panel:login")
def order_status_update(request, order_code):
    order = get_object_or_404(Order, code=order_code)
    new_status = request.POST.get("status")
    try:
        result = update_order_status(order, new_status)
    except ValueError:
        return JsonResponse({"ok": False, "message": "Estado inválido"}, status=400)

    payload = {
        "ok": True,
        "status": result["status_display"],
        "notified": result["notified"],
        "message": result["message"],
    }
    if result["warning"]:
        payload["warning"] = result["warning"]
    return JsonResponse(payload)


@staff_member_required(login_url="admin_panel:login")
@require_POST
def order_notify(request, order_code):
    order = get_object_or_404(Order, code=order_code)
    sent, message = notify_customer(order, force=True)
    if not sent:
        return JsonResponse({"ok": False, "message": message}, status=400)
    return JsonResponse({"ok": True, "message": "Aviso enviado al cliente."})


@staff_member_required(login_url="admin_panel:login")
@require_POST
def order_notify_owner(request, order_code):
    """Reenvía el aviso de nueva compra al administrador."""
    order = get_object_or_404(Order, code=order_code)
    try:
        send_owner_notification(
            order,
            order.receipt_url,
            order.receipt_name,
            None,
            None,
        )
    except Exception as exc:
        logger.exception("No se pudo reenviar el aviso de la orden %s: %s", order.code, exc)
        return JsonResponse(
            {"ok": False, "message": f"No se pudo enviar el correo: {exc}"},
            status=500,
        )

    order.owner_notified_at = timezone.now()
    order.save(update_fields=["owner_notified_at"])
    return JsonResponse({"ok": True, "message": f"Aviso enviado a {settings.ADMIN_EMAIL}."})


@staff_member_required(login_url="admin_panel:login")
@require_POST
def order_delete(request, order_code):
    order = get_object_or_404(Order, code=order_code)
    order.delete()
    return JsonResponse({"ok": True})


@staff_member_required(login_url="admin_panel:login")
def export_orders_xlsx(request):
    """Exporta TODOS los pedidos (no sólo los visibles) con ganancias mensuales."""
    orders = Order.objects.all().order_by("created_at")
    date_from = (request.GET.get("date_from") or "").strip()
    date_to = (request.GET.get("date_to") or "").strip()
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)

    workbook = build_orders_workbook(orders)
    response = HttpResponse(
        workbook.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="reporte-volantines-strong.xlsx"'
    return response
