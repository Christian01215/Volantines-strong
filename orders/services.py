"""Servicios de pedidos: comprobantes, correos y cambios de estado."""
import logging
import mimetypes
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

from config.storage import save_upload

from .models import Order

logger = logging.getLogger(__name__)


STATUS_NOTIFICATIONS = {
    "pago_confirmado": (
        "Pago confirmado",
        ["Recibimos tu comprobante y confirmamos tu pago.", "Seguimos con la preparación de tu pedido."],
    ),
    "preparando": (
        "Estamos preparando tu pedido",
        ["Ya estamos preparando los productos de tu pedido.", "Te avisaremos cuando esté listo para retiro."],
    ),
    "listo_para_retiro": (
        "Tu pedido está listo para retiro",
        ["Ya puedes retirar tu pedido.", "No olvides presentar tu número de pedido."],
    ),
    "retirado": (
        "Pedido retirado",
        ["Tu pedido fue retirado correctamente.", "¡Gracias por comprar en Volantines Strong!"],
    ),
    "cancelado": (
        "Pedido cancelado",
        ["Tu pedido fue cancelado.", "Si tienes dudas, contáctanos por WhatsApp."],
    ),
}


def upload_receipt(receipt, order_code):
    """Guarda el comprobante y devuelve (url, nombre, bytes, mime)."""
    content = receipt.read()
    filename = Path(receipt.name).name
    mimetype = (
        receipt.content_type
        or mimetypes.guess_type(filename)[0]
        or "application/octet-stream"
    )
    path = f"receipts/{order_code}/{filename}"

    result = save_upload(
        content,
        path,
        mimetype,
        settings.SUPABASE_RECEIPTS_BUCKET,
        f"el comprobante del pedido {order_code}",
    )
    return result.final_url, filename, content, mimetype


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
    lines.append(f"Ganancia estimada: ${order.total_profit:,}".replace(",", "."))
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
    ]
    if order.receipt_url:
        lines.append(f"Comprobante: {order.receipt_url}")
    lines.extend([
        "",
        "Puedes consultar el estado en cualquier momento con tu código.",
        "¡Gracias por comprar en Volantines Strong!",
    ])
    _send_customer_email(
        order,
        f"Confirmación de tu pedido {order.code} — Volantines Strong",
        lines,
    )
    return True


def notify_customer(order, status=None, force=False):
    """Avisa al cliente sobre el estado actual.

    Devuelve ``(enviado, mensaje)``. No envía dos veces el mismo estado salvo
    que se use ``force=True`` desde el botón manual "Notificar".
    """
    status = status or order.status
    if not order.customer_email:
        return False, "El pedido no tiene correo electrónico."

    if not force and order.last_notified_status == status:
        return False, "Ya se envió un aviso para este estado."

    title, extra_lines = STATUS_NOTIFICATIONS.get(
        status,
        ("Actualización de tu pedido", [f"Tu pedido está: {order.get_status_display()}."]),
    )
    lines = [
        f"Hola {order.customer_name},",
        "",
        f"Tu pedido {order.code}: {title}.",
        *extra_lines,
        "",
        f"Retira en: {settings.BUSINESS_ADDRESS}",
        f"Fecha y bloque: {order.pickup_date or 'Por confirmar'} {order.pickup_slot}",
        "",
        "¡Gracias por comprar en Volantines Strong!",
    ]
    _send_customer_email(
        order,
        f"{title} — Pedido {order.code} — Volantines Strong",
        lines,
    )
    order.last_notified_status = status
    order.last_notified_at = timezone.now()
    order.save(update_fields=["last_notified_status", "last_notified_at"])
    return True, ""


def send_customer_status_notification(order):
    """Compatibilidad: aviso manual para el estado actual del pedido."""
    return notify_customer(order, order.status, force=True)[0]


def update_order_status(order, new_status, notify=True):
    """Cambia el estado de forma centralizada y evita avisos duplicados."""
    if new_status not in dict(Order.STATUS_CHOICES):
        raise ValueError("Estado inválido")

    previous_status = order.status
    if previous_status == new_status:
        return {
            "changed": False,
            "notified": False,
            "message": "El pedido ya estaba en ese estado.",
            "warning": "",
            "status_display": order.get_status_display(),
        }

    order.status = new_status
    order.save(update_fields=["status"])

    notified = False
    warning = ""
    if notify and new_status in STATUS_NOTIFICATIONS:
        try:
            notified, warning = notify_customer(order, new_status)
        except Exception as exc:
            logger.exception("No se pudo notificar el cambio de estado de %s: %s", order.code, exc)
            warning = f"El estado se actualizó, pero el correo no pudo enviarse: {exc}"

    return {
        "changed": True,
        "notified": notified,
        "message": f"Estado actualizado a {order.get_status_display()}.",
        "warning": warning,
        "status_display": order.get_status_display(),
    }


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
