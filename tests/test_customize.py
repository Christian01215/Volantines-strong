"""RF-09 y seguimiento público de pedidos."""
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from cart.models import CartItem
from cart.services import get_or_create_cart
from orders.models import Order
from products.models import Category, Product


@override_settings(CLOUDINARY_CLOUD_NAME="", CLOUDINARY_API_KEY="", CLOUDINARY_API_SECRET="", CLOUDINARY_URL="")
class CustomizerAndTrackingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.reels = Category.objects.create(name="Carretes", slug="carretes")
        cls.kites = Category.objects.create(name="Volantines", slug="volantines")
        cls.reel = Product.objects.create(
            name="Carrete personalizable",
            slug="carrete-personalizable",
            category=cls.reels,
            price=20000,
            stock=4,
        )
        cls.kite = Product.objects.create(
            name="Volantín normal",
            slug="volantin-normal",
            category=cls.kites,
            price=10000,
            stock=4,
        )

    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.override = override_settings(MEDIA_ROOT=temp_dir.name)
        self.override.enable()
        self.addCleanup(self.override.disable)

    def test_customizer_only_for_reels(self):
        response = self.client.get(reverse("products:customize", args=[self.reel.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "design-canvas")

        response = self.client.get(reverse("products:customize", args=[self.kite.slug]))
        self.assertEqual(response.status_code, 404)

    def test_uploaded_design_travels_with_cart_line(self):
        self.client.get(reverse("cart:api"))
        cart = get_or_create_cart(self.client.get(reverse("cart:api")).wsgi_request)

        response = self.client.post(
            reverse("products:customize_upload", args=[self.reel.slug]),
            {"design": SimpleUploadedFile("mi-diseno.png", b"png-falso", content_type="image/png")},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["design_url"])

        item = CartItem.objects.get(cart=cart, product=self.reel)
        self.assertEqual(item.design_url, payload["design_url"])
        self.assertTrue(item.design_name.endswith(".png"))

    def test_upload_requires_image(self):
        response = self.client.post(
            reverse("products:customize_upload", args=[self.reel.slug]),
            {},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["ok"])

    def test_track_order_by_code(self):
        order = Order.objects.create(
            code="VC87654321",
            customer_name="Cliente",
            total=20000,
            status="listo_para_retiro",
        )
        response = self.client.get(reverse("orders:track"), {"code": order.code})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.code)
        self.assertContains(response, "LISTO PARA RETIRO")

        response = self.client.get(reverse("orders:track_detail", args=[order.code]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("orders:track"), {"code": "VC00000000"})
        self.assertContains(response, "No encontramos un pedido")
