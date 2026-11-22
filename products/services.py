"""Subida de diseños personalizados generados en el canvas."""
import logging
import mimetypes
import uuid
from pathlib import Path

from django.conf import settings

from config.storage import save_upload

logger = logging.getLogger(__name__)


def upload_design(file, slug):
    """Guarda el PNG del personalizador y devuelve ``(url, nombre, error)``."""
    content = file.read()
    extension = Path(file.name).suffix.lower() or ".png"
    filename = f"{slug}-{uuid.uuid4().hex[:10]}{extension}"
    mimetype = file.content_type or mimetypes.guess_type(filename)[0] or "image/png"
    path = f"designs/{slug}/{filename}"

    result = save_upload(
        content,
        path,
        mimetype,
        settings.SUPABASE_DESIGNS_BUCKET,
        f"el diseño de {slug}",
    )
    return result.final_url, filename, result.error
