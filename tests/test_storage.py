"""Pruebas de la capa centralizada de subida a Supabase Storage."""
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from config.storage import StorageUploadError, save_upload


@override_settings(
    SUPABASE_URL="https://example.supabase.co",
    SUPABASE_KEY="service-role-test-key",
    SUPABASE_STORAGE_BUCKET="product-images",
    SUPABASE_RECEIPTS_BUCKET="payment-receipts",
    ALLOW_LOCAL_STORAGE_FALLBACK=False,
)
class StorageUploadTests(TestCase):
    def test_upload_is_explicitly_not_upsert(self):
        client = MagicMock()
        bucket = client.storage.from_.return_value
        bucket.get_public_url.return_value = "https://example.supabase.co/receipt.png"

        with patch("config.storage.supabase.create_client", return_value=client):
            result = save_upload(
                b"contenido", "receipts/VC1/receipt.png", "image/png",
                "payment-receipts", "el comprobante del pedido VC1",
            )

        client.storage.from_.assert_called_once_with("payment-receipts")
        args = bucket.upload.call_args.args
        self.assertEqual(args[0], "receipts/VC1/receipt.png")
        self.assertEqual(args[1], b"contenido")
        self.assertEqual(args[2]["content-type"], "image/png")
        self.assertEqual(args[2]["x-upsert"], "false")
        self.assertEqual(result.url, "https://example.supabase.co/receipt.png")

    def test_rls_error_explains_service_role_requirement(self):
        rls_error = (
            "{'statusCode': 403, 'error': 'Unauthorized', "
            "'message': 'new row violates row-level security policy'}"
        )

        with patch("config.storage.supabase.create_client", side_effect=Exception(rls_error)):
            with self.assertRaises(StorageUploadError) as raised:
                save_upload(
                    b"contenido", "receipts/VC1/receipt.png", "image/png",
                    "payment-receipts", "el comprobante del pedido VC1",
                )

        message = str(raised.exception)
        self.assertIn("payment-receipts", message)
        self.assertIn("service_role", message)
        self.assertIn("RLS", message)
