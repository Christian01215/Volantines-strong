"""Validaciones compartidas de datos del comprador y archivos subidos."""
import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

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
    expected = "0" if remainder == 0 else "K" if remainder == 10 else str(11 - remainder)
    return expected == verifier


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
