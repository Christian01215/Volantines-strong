"""Servicios de pedidos: comprobantes y aviso por correo al administrador."""
import logging
import mimetypes
from pathlib import Path

import supabase
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


def upload_receipt(receipt, order_code):
    """Guarda el comprobante y devuelve (url, nombre, bytes, mime)."""
    content = receipt.read()
    filename = Path(receipt.name).name
    mimetype = receipt.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    path = f"receipts/{order_code}/{filename}"

    if settings.SUPABASE_URL and settings.SUPABASE_KEY and settings.SUPABASE_RECEIPTS_BUCKET:
        try:
            client = supabase.create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            bucket = client.storage.from_(settings.SUPABASE_RECEIPTS_BUCKET)
            bucket.upload(path, content, {"content-type": mimetype})
            return bucket.get_public_url(path), filename, content, mimetype
        except Exception as exc:
            logger.warning("No se pudo subir el comprobante a Supabase: %s", exc)

    local_path = default_storage.save(path, ContentFile(content))
    return default_storage.url(local_path), filename, content, mimetype


def send_owner_notification(order, receipt_url, receipt_name, receipt_content, receipt_mimetype):
    """Envía al dueño el detalle del pedido con el comprobante adjunto."""
    recipient = settings.ADMIN_EMAIL or settings.DEFAULT_FROM_EMAIL
    if not settings.ADMIN_EMAIL:
        logger.warning("ADMIN_EMAIL no está configurado; el aviso se envía a DEFAULT_FROM_EMAIL")

    lines = [
        f"Orden: {order.code}",
        f"Cliente: {order.customer_name}",
        f"RUT: {order.customer_rut}",
        f"Teléfono: {order.customer_phone}",
        f"Correo: {order.customer_email}",
        "",
        f"Entrega: {order.get_delivery_type_display()}",
        f"Fecha: {order.pickup_date or '-'} {order.pickup_slot}",
        f"Región/Comuna: {order.delivery_region} / {order.delivery_commune}",
        f"Dirección: {order.delivery_address or '-'}",
        "",
        "Productos:",
    ]
    for item in order.items.select_related("product"):
        lines.append(f"- {item.product.name} x{item.quantity} — ${item.line_total:,}".replace(",", "."))
    lines.append("")
    lines.append(f"Total: ${order.total:,}".replace(",", "."))
    lines.append(f"Medio de pago informado: {order.payment_method or 'transferencia'}")
    if order.payment_method == "transferencia":
        lines.append(
            "Datos de transferencia: "
            f"{settings.BANK_NAME} · {settings.BANK_ACCOUNT_TYPE} · "
            f"Titular Volantines Strong · RUT {settings.BANK_RUT or 'por configurar'} · "
            f"Cuenta {settings.BANK_ACCOUNT or 'por configurar'}"
        )
    lines.append(f"Comprobante: {receipt_url}")

    text_body = "\n".join(lines)
    html_body = "<br>".join(f"<span>{line}</span>" for line in lines) + (
        f'<br><br><a href="{receipt_url}">Ver comprobante adjunto</a>'
    )

    email = EmailMultiAlternatives(
        subject=f"Nueva compra {order.code} — Volantines Strong",
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    email.attach_alternative(html_body, "text/html")
    if receipt_content and receipt_name:
        email.attach(receipt_name, receipt_content, receipt_mimetype or "application/octet-stream")
    email.send(fail_silently=False)


def send_customer_confirmation(order):
    """Confirmación automática al comprador con el código y datos de retiro."""
    if not order.customer_email:
        return False

    lines = [
        f"Hola {order.customer_name},",
        "",
        f"Recibimos tu pedido {order.code} y tu comprobante de pago.",
        "Te avisaremos cuando esté listo para retiro.",
        "",
        f"Total: ${order.total:,}".replace(",", "."),
        f"Retiro: {settings.BUSINESS_ADDRESS}",
        f"Fecha: {order.pickup_date or 'Por confirmar'} {order.pickup_slot}",
        "",
        "Puedes consultar el estado en cualquier momento con tu código.",
        "¡Gracias por comprar en Volantines Strong!",
    ]
    _send_customer_email(
        order,
        f"Confirmación de tu pedido {order.code} — Volantines Strong",
        lines,
    )
    return True


def send_customer_status_notification(order):
    """Aviso automático cuando el pedido pasa a 'Listo para Retiro'."""
    if not order.customer_email:
        return False

    lines = [
        f"Hola {order.customer_name},",
        "",
        f"Tu pedido {order.code} ya está listo para retiro.",
        "",
        f"Retira en: {settings.BUSINESS_ADDRESS}",
        f"Fecha y bloque: {order.pickup_date or 'Por confirmar'} {order.pickup_slot}",
        "No olvides presentar tu número de pedido.",
        "",
        "¡Gracias por comprar en Volantines Strong!",
    ]
    _send_customer_email(
        order,
        f"Tu pedido {order.code} está listo — Volantines Strong",
        lines,
    )
    return True


def _send_customer_email(order, subject, lines):
    text_body = "\n".join(lines)
    html_body = "<br>".join(f"<span>{line}</span>" for line in lines)
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.customer_email],
    )
    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)
