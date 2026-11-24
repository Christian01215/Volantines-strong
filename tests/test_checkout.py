"""Flujo completo de compra: carrito en BD, orden, stock y correo al dueño."""
from datetime import timedelta

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from cart.models import CartItem
from cart.services import get_or_create_cart
from orders.models import Order
from products.models import Category, Product


@override_settings(
    CLOUDINARY_CLOUD_NAME="",
    CLOUDINARY_API_KEY="",
    CLOUDINARY_API_SECRET="",
    CLOUDINARY_URL="",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class CheckoutFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Carretes", slug="carretes")
        cls.product = Product.objects.create(
            name="Carrete prueba",
            slug="carrete-prueba",
            category=cls.category,
            price=25000,
            stock=10,
        )

    def _fill_cart(self, quantity=2):
        self.client.post(
            reverse("cart:api_add"),
            {"product_id": self.product.pk, "quantity": quantity},
        )

    def _checkout_payload(self):
        return {
            "customer_name": "Ana Prueba",
            "customer_rut": "12.345.678-5",
            "customer_phone": "+56 9 1234 5678",
            "customer_email": "ana@example.com",
            "pickup_date": (timezone.localdate() + timedelta(days=7)).isoformat(),
            "pickup_slot": "10:00 - 12:00",
            "receipt": SimpleUploadedFile(
                "comprobante.png", b"contenido-falso", content_type="image/png"
            ),
        }

    def _post_checkout(self, payload):
        return self.client.post(
            reverse("orders:checkout"),
            payload,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

    def test_checkout_creates_order_discounts_stock_and_empties_cart(self):
        mail.outbox = []
        self._fill_cart(2)

        response = self.client.post(
            reverse("orders:checkout"),
            self._checkout_payload(),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["code"].startswith("VC"))
        self.assertEqual(len(payload["code"]), 10)

        order = Order.objects.get(code=payload["code"])
        self.assertEqual(order.status, "pendiente")
        self.assertEqual(order.delivery_type, "click_collect")
        self.assertEqual(order.total, 50000)
        self.assertEqual(order.items.count(), 1)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)

        cart_response = self.client.get(reverse("cart:api"))
        self.assertEqual(cart_response.json()["count"], 0)

        # Dueño y comprador reciben correo; el primero lleva el comprobante adjunto.
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ["ctorresj@utem.cl"])
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(mail.outbox[1].to, ["ana@example.com"])
        self.assertIn(order.code, mail.outbox[1].subject)

    def test_checkout_accepts_ruts_ending_in_one_and_k(self):
        for rut in ("12.345.604-1", "12.345.605-K"):
            with self.subTest(rut=rut):
                self._fill_cart(1)
                payload = self._checkout_payload()
                payload["customer_rut"] = rut

                response = self._post_checkout(payload)

                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["ok"])
                self.assertTrue(Order.objects.filter(customer_rut=rut).exists())

    def test_checkout_requires_pickup_date_and_slot(self):
        self._fill_cart(1)
        payload = self._checkout_payload()
        payload.pop("pickup_date")
        payload.pop("pickup_slot")

        response = self._post_checkout(payload)

        self.assertEqual(response.status_code, 400)
        message = response.json()["message"]
        self.assertFalse(response.json()["ok"])
        self.assertIn("fecha de retiro", message)
        self.assertIn("bloque horario de retiro", message)
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_rejects_empty_pickup_slot(self):
        self._fill_cart(1)
        payload = self._checkout_payload()
        payload["pickup_slot"] = ""

        response = self._post_checkout(payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("bloque horario de retiro", response.json()["message"])
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_rejects_past_pickup_date(self):
        self._fill_cart(1)
        payload = self._checkout_payload()
        payload["pickup_date"] = (
            timezone.localdate() - timedelta(days=1)
        ).isoformat()

        response = self._post_checkout(payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("anterior a hoy", response.json()["message"])
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_rejects_unknown_pickup_slot(self):
        self._fill_cart(1)
        payload = self._checkout_payload()
        payload["pickup_slot"] = "23:00 - 00:00"

        response = self._post_checkout(payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("bloque horario de retiro no es válido", response.json()["message"])
        self.assertEqual(Order.objects.count(), 0)

    def test_customer_confirmation_can_be_disabled(self):
        mail.outbox = []
        self._fill_cart(1)

        with self.settings(SEND_CUSTOMER_CONFIRMATION=False):
            response = self.client.post(
                reverse("orders:checkout"),
                self._checkout_payload(),
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )

        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["customer_email_sent"])
        self.assertTrue(Order.objects.filter(code=payload["code"]).exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["ctorresj@utem.cl"])

    def test_checkout_rejects_empty_cart(self):
        response = self.client.post(
            reverse("orders:checkout"),
            self._checkout_payload(),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["ok"])
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_rejects_quantity_above_stock(self):
        # Se fuerza una cantidad imposible para simular un cambio de stock
        # entre que el cliente agregó el producto y confirmó la compra.
        cart = get_or_create_cart(self.client.get(reverse("cart:api")).wsgi_request)
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=20,
            price_at_time=self.product.price,
        )
        response = self.client.post(
            reverse("orders:checkout"),
            self._checkout_payload(),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)

    def test_checkout_rejects_invalid_rut_and_receipt_type(self):
        self._fill_cart(1)
        payload = self._checkout_payload()
        payload["customer_rut"] = "12.345.678-9"
        response = self.client.post(
            reverse("orders:checkout"),
            payload,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("RUT", response.json()["message"])

        payload = self._checkout_payload()
        payload["receipt"] = SimpleUploadedFile(
            "virus.exe", b"malicioso", content_type="application/octet-stream"
        )
        response = self.client.post(
            reverse("orders:checkout"),
            payload,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Formato no permitido", response.json()["message"])
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_snapshots_product_cost_for_profit(self):
        self.product.cost = 10000
        self.product.save(update_fields=["cost"])
        self._fill_cart(2)

        response = self.client.post(
            reverse("orders:checkout"),
            self._checkout_payload(),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        order = Order.objects.get(code=response.json()["code"])
        item = order.items.get()

        self.assertEqual(item.cost, 10000)
        self.assertEqual(item.line_profit, 30000)
        self.assertEqual(order.total_profit, 30000)

    def test_storage_failure_returns_json_instead_of_html_500(self):
        self._fill_cart(1)
        with self.settings(
            ALLOW_LOCAL_STORAGE_FALLBACK=False,
            CLOUDINARY_CLOUD_NAME="",
            CLOUDINARY_API_KEY="",
            CLOUDINARY_API_SECRET="",
            CLOUDINARY_URL="",
        ):
            response = self.client.post(
                reverse("orders:checkout"),
                self._checkout_payload(),
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )

        self.assertEqual(response.status_code, 500)
        self.assertIn("application/json", response["Content-Type"])
        self.assertFalse(response.json()["ok"])
        self.assertEqual(Order.objects.count(), 0)

    def test_track_and_success_pages_show_products_and_receipt(self):
        self._fill_cart(1)
        response = self.client.post(
            reverse("orders:checkout"),
            self._checkout_payload(),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        payload = response.json()
        code = payload["code"]

        success = self.client.get(reverse("orders:success", args=[code]))
        self.assertEqual(success.status_code, 200)
        self.assertContains(success, "Carrete prueba")
        self.assertContains(success, "Ver comprobante de pago")
        self.assertContains(success, '<tbody class="text-slate-900">')

        track = self.client.get(reverse("orders:track_detail", args=[code]))
        self.assertEqual(track.status_code, 200)
        self.assertContains(track, "Carrete prueba")
        self.assertContains(track, "Productos comprados")
        self.assertContains(track, "Ver comprobante de pago")
        self.assertContains(track, '<tbody class="text-slate-900">')
        self.assertTrue(payload["receipt_url"])

    def test_success_page(self):
        self._fill_cart(1)
        response = self.client.post(
            reverse("orders:checkout"),
            self._checkout_payload(),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        code = response.json()["code"]
        page = self.client.get(reverse("orders:success", args=[code]))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, code)
