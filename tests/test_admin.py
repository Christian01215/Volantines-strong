"""Panel de administración: permisos, slug único y rutas de pedidos."""
from datetime import date, timedelta
from io import BytesIO
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from openpyxl import load_workbook

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

    def test_status_changes_notify_each_transition_once(self):
        order = Order.objects.create(
            code="VC66666666",
            customer_name="Cliente Estados",
            customer_email="estados@example.com",
            total=15000,
        )
        url = reverse("admin_panel:order_status_update", args=[order.code])

        for status in ["pago_confirmado", "preparando", "listo_para_retiro"]:
            response = self.client.post(url, {"status": status})
            self.assertTrue(response.json()["ok"])

        self.assertEqual(len(mail.outbox), 3)
        subjects = " ".join(message.subject for message in mail.outbox)
        self.assertIn("Pago confirmado", subjects)
        self.assertIn("preparando", subjects.lower())
        self.assertIn("listo", subjects.lower())

        # Repetir el mismo estado no genera otro correo.
        self.client.post(url, {"status": "listo_para_retiro"})
        self.assertEqual(len(mail.outbox), 3)

    def test_product_delete_is_soft_and_can_be_restored(self):
        product = Product.objects.create(
            name="Producto temporal",
            slug="producto-temporal",
            category=self.category,
            price=1000,
            cost=400,
            stock=2,
        )
        delete_url = reverse("admin_panel:product_delete", args=[product.pk])
        restore_url = reverse("admin_panel:product_restore", args=[product.pk])

        response = self.client.post(delete_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        product.refresh_from_db()
        self.assertFalse(product.is_active)

        catalog = self.client.get(reverse("products:catalog"))
        visible_names = [item.name for item in catalog.context["products"]]
        self.assertNotIn("Producto temporal", visible_names)

        response = self.client.post(restore_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertTrue(response.json()["ok"])
        product.refresh_from_db()
        self.assertTrue(product.is_active)

    def test_owner_notification_retry_sets_timestamp(self):
        order = Order.objects.create(
            code="VC77777777",
            customer_name="Cliente Aviso Dueño",
            total=12000,
            receipt_url="https://example.com/comprobante.png",
        )
        url = reverse("admin_panel:order_notify_owner", args=[order.code])

        response = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        order.refresh_from_db()
        self.assertIsNotNone(order.owner_notified_at)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["ctorresj@utem.cl"])

    def test_export_orders_xlsx_includes_profit_summary(self):
        product = Product.objects.create(
            name="Producto Excel",
            slug="producto-excel",
            category=self.category,
            price=10000,
            cost=6000,
            stock=3,
        )
        order = Order.objects.create(
            code="VC88888888",
            customer_name="Cliente Excel",
            total=20000,
        )
        OrderItem.objects.create(
            order=order, product=product, quantity=2, price=10000, cost=6000
        )

        response = self.client.get(reverse("admin_panel:export_orders"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("spreadsheetml.sheet", response["Content-Type"])
        workbook = load_workbook(BytesIO(response.content))
        self.assertEqual(
            workbook.sheetnames,
            ["Resumen mensual", "Pedidos", "Detalle por producto", "Categorías"],
        )
        detail = workbook["Detalle por producto"]
        self.assertEqual(detail["I2"].value, 8000)
        categories = workbook["Categorías"]
        self.assertEqual(categories["D2"].value, 8000)

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
