"""Subida centralizada de archivos a Cloudinary.

Toda subida pasa por aquí para que el comportamiento sea el mismo en productos,
comprobantes y diseños: en producción se exige Cloudinary; en desarrollo se
permite un fallback local controlado.
"""
import io
import logging
from dataclasses import dataclass
from pathlib import Path

import cloudinary
import cloudinary.uploader
from django.conf import settings
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


class StorageUploadError(Exception):
    """Error de subida con un mensaje apto para mostrar al usuario."""


@dataclass
class UploadResult:
    """Resultado de guardar un archivo.

    ``url`` es la URL pública cuando se sube a Cloudinary. Cuando se usa el
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
            return self.local_path
        return ""


def _cloudinary_configured():
    cloud_name = getattr(settings, "CLOUDINARY_CLOUD_NAME", "")
    api_key = getattr(settings, "CLOUDINARY_API_KEY", "")
    api_secret = getattr(settings, "CLOUDINARY_API_SECRET", "")
    cloudinary_url = getattr(settings, "CLOUDINARY_URL", "")
    return bool(cloudinary_url or (cloud_name and api_key and api_secret))


def _configure_cloudinary():
    cloudinary_url = getattr(settings, "CLOUDINARY_URL", "")
    if cloudinary_url:
        cloudinary.config(cloudinary_url=cloudinary_url, secure=True)
        return
    cloudinary.config(
        cloud_name=getattr(settings, "CLOUDINARY_CLOUD_NAME", ""),
        api_key=getattr(settings, "CLOUDINARY_API_KEY", ""),
        api_secret=getattr(settings, "CLOUDINARY_API_SECRET", ""),
        secure=True,
    )


def _public_id(path):
    # Cloudinary agrega la extensión según el formato; el public_id no debe
    # incluirla para evitar duplicados tipo "foo.png.png".
    return Path(path).with_suffix("").as_posix()


def save_upload(content, path, mimetype, bucket="", label="el archivo"):
    """Sube ``content`` a Cloudinary y devuelve un ``UploadResult``.

    ``bucket`` se conserva por compatibilidad con la API anterior de Supabase
    pero no se usa: Cloudinary organiza los recursos por carpetas dentro del
    ``public_id`` (que ya incluye la ruta).
    """
    del bucket  # compatibilidad con la firma anterior

    # Normalizar content a bytes.
    if isinstance(content, (bytes, bytearray)):
        data = bytes(content)
    else:
        try:
            content.seek(0)
        except Exception:
            pass
        data = content.read() if hasattr(content, "read") else bytes(content)

    if not _cloudinary_configured():
        if getattr(settings, "ALLOW_LOCAL_STORAGE_FALLBACK", False):
            saved_path = default_storage.save(path, content if not isinstance(content, (bytes, bytearray)) else __import__("django.core.files.base", fromlist=["ContentFile"]).ContentFile(data))
            return UploadResult(local_path=saved_path)
        raise StorageUploadError(
            f"No se pudo subir {label}: Cloudinary no está configurado "
            "y el fallback local está desactivado."
        )

    try:
        _configure_cloudinary()
        public_id = _public_id(path)
        result = cloudinary.uploader.upload(
            io.BytesIO(data),
            public_id=public_id,
            resource_type="auto",
            overwrite=False,
            unique_filename=False,
            use_filename=False,
            format=None,
        )
        url = result.get("secure_url") or result.get("url") or ""
        if not url:
            raise StorageUploadError(f"No se obtuvo URL pública para {label}.")
        return UploadResult(url=url)
    except StorageUploadError:
        raise
    except Exception as exc:
        logger.exception("Error subiendo %s a Cloudinary", label)
        message = getattr(exc, "message", None) or str(exc)
        raise StorageUploadError(f"No se pudo subir {label} a Cloudinary: {message}")
