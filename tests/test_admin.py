"""Panel de administración: permisos, slug único y rutas de pedidos."""
from datetime import date, timedelta
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from orders.models import Order, OrderItem
from products.models import Category, Product


class AdminPanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user(
            username="admin", password="clave-segura-123", is_staff=True
        )
        cls.category = Category.objects.create(name="Volantines", slug="volantines")

    def setUp(self):
        mail.outbox = []
        self.client.force_login(self.staff)

    def test_dashboard_renders(self):
        response = self.client.get(reverse("admin_panel:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VOLANTINES STRONG")

    def test_repeated_product_name_creates_unique_slugs(self):
        data = {
            "prod_name": "Volantín Strong Grande",
            "prod_category": str(self.category.pk),
            "prod_price": "15000",
            "prod_stock": "5",
            "prod_specs": "Medida 120 cm",
            "prod_desc": "Competición",
        }
        self.client.post(reverse("admin_panel:product_save"), data)
        self.client.post(reverse("admin_panel:product_save"), data)

        products = Product.objects.filter(name=data["prod_name"]).order_by("pk")
        self.assertEqual(products.count(), 2)
        self.assertNotEqual(products[0].slug, products[1].slug)

    def test_product_creation_saves_main_image_and_gallery(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        with self.settings(MEDIA_ROOT=temp_dir.name, SUPABASE_URL="", SUPABASE_KEY=""):
            response = self.client.post(
                reverse("admin_panel:product_save"),
                {
                    "prod_name": "Carrete con fotos",
                    "prod_category": str(self.category.pk),
                    "prod_price": "18000",
                    "prod_stock": "6",
                    "prod_specs": "Madera",
                    "prod_image_file": SimpleUploadedFile(
                        "principal.png", b"png-principal", content_type="image/png"
                    ),
                    "prod_gallery_files": [
                        SimpleUploadedFile("g1.png", b"png-1", content_type="image/png"),
                        SimpleUploadedFile("g2.png", b"png-2", content_type="image/png"),
                    ],
                },
            )

        self.assertEqual(response.status_code, 302)
        product = Product.objects.get(name="Carrete con fotos")
        self.assertTrue(product.image.name.startswith("products/"))
        self.assertNotIn("/media/media/", product.image.url)
        self.assertEqual(product.gallery.count(), 2)

    def test_order_list_and_status_update(self):
        order = Order.objects.create(
            code="VC12345678",
            customer_name="Cliente",
            total=10000,
        )
        response = self.client.get(reverse("orders:admin_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.code)

        response = self.client.post(
            reverse("orders:admin_update", args=[order.code]),
            {"status": "pago_confirmado"},
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, "pago_confirmado")

    def test_ready_for_pickup_sends_customer_notification_once(self):
        order = Order.objects.create(
            code="VC55555555",
            customer_name="Cliente Aviso",
            customer_email="cliente@example.com",
            total=15000,
            pickup_date=date.today() + timedelta(days=2),
            pickup_slot="10:00 - 12:00",
        )
        url = reverse("admin_panel:order_status_update", args=[order.code])

        self.client.post(url, {"status": "listo_para_retiro"})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["cliente@example.com"])
        self.assertIn(order.code, mail.outbox[0].subject)

        self.client.post(url, {"status": "listo_para_retiro"})
        self.assertEqual(len(mail.outbox), 1)

    def test_reports_in_dashboard(self):
        product = Product.objects.create(
            name="Producto reporte",
            slug="producto-reporte",
            category=self.category,
            price=10000,
            stock=3,
        )
        order = Order.objects.create(
            code="VC44444444",
            customer_name="Cliente Reporte",
            total=20000,
            status="pago_confirmado",
            pickup_date=date.today() + timedelta(days=1),
        )
        OrderItem.objects.create(order=order, product=product, quantity=2, price=10000)

        response = self.client.get(reverse("admin_panel:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("status_counts", response.context)
        self.assertIn("category_sales", response.context)
        self.assertIn("upcoming_pickups", response.context)
        self.assertEqual(
            response.context["category_sales"][0]["revenue"], 20000
        )
        self.assertContains(response, "04 / REPORTES")

    def test_non_staff_cannot_access_dashboard(self):
        user = User.objects.create_user(username="cliente", password="clave-123")
        self.client.force_login(user)
        response = self.client.get(reverse("admin_panel:dashboard"))
        self.assertEqual(response.status_code, 302)
