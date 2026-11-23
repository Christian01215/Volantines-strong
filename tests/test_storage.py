"""Pruebas de la capa centralizada de subida a Cloudinary."""
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from config.storage import StorageUploadError, save_upload


@override_settings(
    CLOUDINARY_CLOUD_NAME="demo",
    CLOUDINARY_API_KEY="key",
    CLOUDINARY_API_SECRET="secret",
    CLOUDINARY_URL="",
    ALLOW_LOCAL_STORAGE_FALLBACK=False,
)
class StorageUploadTests(TestCase):
    def test_upload_returns_secure_url(self):
        fake_result = {"secure_url": "https://res.cloudinary.com/demo/image/upload/v1/receipt.png"}

        with patch("config.storage.cloudinary.uploader.upload", return_value=fake_result) as upload:
            result = save_upload(
                b"contenido", "receipts/VC1/receipt.png", "image/png",
                "", "el comprobante del pedido VC1",
            )

        self.assertEqual(result.url, "https://res.cloudinary.com/demo/image/upload/v1/receipt.png")
        upload.assert_called_once()
        # No se fuerza sobrescritura (no upsert).
        self.assertFalse(upload.call_args.kwargs.get("overwrite", False))

    def test_upload_error_raises_storage_upload_error(self):
        with patch("config.storage.cloudinary.uploader.upload", side_effect=Exception("boom")):
            with self.assertRaises(StorageUploadError):
                save_upload(
                    b"contenido", "receipts/VC1/receipt.png", "image/png",
                    "", "el comprobante del pedido VC1",
                )

    def test_local_fallback_when_not_configured(self):
        with override_settings(ALLOW_LOCAL_STORAGE_FALLBACK=True, CLOUDINARY_CLOUD_NAME="", CLOUDINARY_API_KEY="", CLOUDINARY_API_SECRET="", CLOUDINARY_URL=""):
            with patch("config.storage.default_storage.save", return_value="receipts/VC1/receipt.png"):
                result = save_upload(
                    b"contenido", "receipts/VC1/receipt.png", "image/png",
                    "", "el comprobante del pedido VC1",
                )
        self.assertEqual(result.local_path, "receipts/VC1/receipt.png")
        self.assertEqual(result.url, "")
