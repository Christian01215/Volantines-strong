"""Validaciones compartidas de datos del comprador y archivos subidos."""
import re
from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone

MAX_RECEIPT_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_DESIGN_SIZE = 3 * 1024 * 1024  # 3 MB
MAX_IMAGE_SIZE = 3 * 1024 * 1024  # 3 MB por imagen de producto

RECEIPT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
}
DESIGN_TYPES = {"image/jpeg", "image/png", "image/webp"}
IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

PICKUP_SLOTS = (
    "10:00 - 12:00",
    "12:00 - 14:00",
    "15:00 - 17:00",
    "17:00 - 19:00",
)


def validate_upload(upload, allowed_types, max_size, label):
    """Devuelve un mensaje de error o None si el archivo es válido."""
    if upload.size > max_size:
        return f"{label} demasiado grande. Máximo {max_size // (1024 * 1024)} MB."
    mimetype = (upload.content_type or "").lower()
    if mimetype not in allowed_types:
        return f"Formato no permitido para {label}. Usa {', '.join(sorted(allowed_types))}."
    return None


def validate_rut(value):
    """Valida un RUT chileno en formato 12.345.678-9 o 123456789."""
    raw = re.sub(r"[^0-9kK]", "", value or "")
    if len(raw) < 8 or len(raw) > 9:
        return False

    body, verifier = raw[:-1], raw[-1].upper()
    multiplier = 2
    total = 0
    for digit in reversed(body):
        total += int(digit) * multiplier
        multiplier = multiplier + 1 if multiplier < 7 else 2

    remainder = total % 11
    expected = "0" if remainder == 0 else "K" if remainder == 1 else str(11 - remainder)
    return expected == verifier


def validate_pickup_data(data):
    """Devuelve errores si falta o es inválida la fecha/bloque de retiro."""
    errors = []
    raw_date = (data.get("pickup_date") or "").strip()
    if not raw_date:
        errors.append("Debe elegir una fecha de retiro.")
    else:
        try:
            pickup_date = date.fromisoformat(raw_date)
        except ValueError:
            errors.append("La fecha de retiro no es válida.")
        else:
            if pickup_date < timezone.localdate():
                errors.append("La fecha de retiro no puede ser anterior a hoy.")

    slot = (data.get("pickup_slot") or "").strip()
    if not slot:
        errors.append("Debe elegir un bloque horario de retiro.")
    elif slot not in PICKUP_SLOTS:
        errors.append("El bloque horario de retiro no es válido.")
    return errors


def validate_customer_data(data):
    """Devuelve una lista de errores de los datos obligatorios del checkout."""
    errors = []
    if not validate_rut(data.get("customer_rut", "")):
        errors.append("El RUT no es válido.")
    try:
        validate_email(data.get("customer_email", ""))
    except ValidationError:
        errors.append("El correo electrónico no es válido.")
    if len((data.get("customer_phone") or "").strip()) < 8:
        errors.append("El teléfono no es válido.")
    return errors
