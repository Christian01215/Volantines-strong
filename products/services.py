"""Subida de diseños personalizados generados en el canvas."""
import logging
import mimetypes
import uuid
from pathlib import Path

import supabase
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


def upload_design(file, slug):
    """Guarda el PNG del personalizador y devuelve ``(url, nombre, error)``."""
    content = file.read()
    extension = Path(file.name).suffix.lower() or ".png"
    filename = f"{slug}-{uuid.uuid4().hex[:10]}{extension}"
    mimetype = (
        file.content_type
        or mimetypes.guess_type(filename)[0]
        or "image/png"
    )
    path = f"designs/{slug}/{filename}"

    if settings.SUPABASE_URL and settings.SUPABASE_KEY and settings.SUPABASE_DESIGNS_BUCKET:
        try:
            client = supabase.create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            bucket = client.storage.from_(settings.SUPABASE_DESIGNS_BUCKET)
            bucket.upload(path, content, {"content-type": mimetype})
            return bucket.get_public_url(path), filename, None
        except Exception as exc:
            logger.warning("No se pudo subir el diseño a Supabase: %s", exc)
            error = str(exc)
    else:
        error = None

    local_path = default_storage.save(path, ContentFile(content))
    return default_storage.url(local_path), filename, error
