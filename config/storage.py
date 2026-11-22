"""Subida centralizada de archivos a Supabase Storage.

Toda subida pasa por aquí para que el comportamiento sea el mismo en productos,
comprobantes y diseños: en producción se exige Supabase; en desarrollo se
permite un fallback local controlado.
"""
import logging
from dataclasses import dataclass

import supabase
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


class StorageUploadError(Exception):
    """Error de subida con un mensaje apto para mostrar al usuario."""


@dataclass
class UploadResult:
    """Resultado de guardar un archivo.

    ``url`` es la URL pública cuando se sube a Supabase. Cuando se usa el
    fallback local, ``local_path`` tiene la ruta y ``url`` queda vacía.
    """

    url: str = ""
    local_path: str = ""
    error: str = ""

    @property
    def final_url(self):
        if self.url:
            return self.url
        if self.local_path:
            return default_storage.url(self.local_path)
        return ""

    @property
    def used_local(self):
        return bool(self.local_path)


def _fallback_allowed():
    return bool(getattr(settings, "ALLOW_LOCAL_STORAGE_FALLBACK", False))


def save_upload(content, path, mimetype, bucket, label):
    """Guarda ``content`` en ``bucket`` y devuelve :class:`UploadResult`.

    Si Supabase no está configurado o falla, sólo se usa almacenamiento local
    cuando ``ALLOW_LOCAL_STORAGE_FALLBACK`` está activo. De lo contrario se
    lanza :class:`StorageUploadError` con un mensaje claro.
    """
    mimetype = mimetype or "application/octet-stream"
    error = ""

    if settings.SUPABASE_URL and settings.SUPABASE_KEY and bucket:
        try:
            client = supabase.create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            storage_bucket = client.storage.from_(bucket)
            storage_bucket.upload(path, content, {"content-type": mimetype})
            return UploadResult(url=storage_bucket.get_public_url(path))
        except Exception as exc:
            error = str(exc)
            logger.exception("No se pudo subir %s al bucket '%s': %s", label, bucket, exc)
            if not _fallback_allowed():
                raise StorageUploadError(
                    f"No se pudo subir {label} a Supabase Storage ({bucket}): {error}"
                ) from exc
    else:
        error = f"Supabase Storage no está configurado para {label}."
        logger.warning(error)
        if not _fallback_allowed():
            raise StorageUploadError(
                f"{error} Configura SUPABASE_URL, SUPABASE_KEY y el bucket en Vercel."
            )

    try:
        local_path = default_storage.save(path, ContentFile(content))
    except Exception as exc:
        logger.exception("No se pudo guardar %s en almacenamiento local: %s", label, exc)
        raise StorageUploadError(
            f"No se pudo guardar {label}: {exc}. Revisa la configuración de Storage."
        ) from exc

    return UploadResult(local_path=local_path, error=error)
