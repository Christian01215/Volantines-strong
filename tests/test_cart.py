"""Cantidades libres en el carrito y texto del botón de registro."""
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product


class CartQuantityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Carretes", slug="carretes")
        cls.product = Product.objects.create(
            name="Carrete cantidad",
            slug="carrete-cantidad",
            category=cls.category,
            price=25000,
            stock=5,
        )

    def _api_add(self, quantity):
        return self.client.post(
            reverse("cart:api_add"),
            {"product_id": self.product.pk, "quantity": quantity},
        )

    def _cart_count(self):
        return self.client.get(reverse("cart:api")).json()["count"]

    def test_api_add_accepts_exact_quantity(self):
        response = self._api_add(3)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(response.json()["count"], 3)
        self.assertEqual(self._cart_count(), 3)

    def test_api_add_accumulates_until_stock(self):
        self._api_add(2)
        response = self._api_add(3)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(response.json()["count"], 5)

    def test_api_add_over_stock_returns_clear_error(self):
        response = self._api_add(100)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["ok"])
        self.assertIn("Solo quedan 5 unidades", response.json()["message"])
        self.assertEqual(self._cart_count(), 0)

    def test_api_update_sets_exact_quantity(self):
        self._api_add(2)
        response = self.client.post(
            reverse("cart:api_update"),
            {"product_id": self.product.pk, "quantity": 4},
        )
        self.assertEqual(response.json()["count"], 4)
        self.assertEqual(self._cart_count(), 4)

    def test_html_set_quantity_view(self):
        self._api_add(2)
        response = self.client.post(
            reverse("cart:set_quantity", args=[self.product.pk]),
            {"quantity": 4},
        )
        self.assertRedirects(response, reverse("cart:view"))
        self.assertEqual(self._cart_count(), 4)

    def test_cart_page_shows_editable_quantity(self):
        self._api_add(2)
        response = self.client.get(reverse("cart:view"))
        self.assertContains(response, 'type="number"')
        self.assertContains(response, 'name="quantity"')
        self.assertContains(response, 'value="2"')

    def test_quantity_inputs_and_clean_submit_label(self):
        catalog = self.client.get(reverse("products:catalog"))
        self.assertContains(catalog, 'id="modal-qty"')
        self.assertContains(catalog, "Registrar pedido")
        self.assertNotContains(catalog, "pago pendiente")

        detail = self.client.get(reverse("products:detail", args=[self.product.slug]))
        self.assertContains(detail, 'id="detail-qty"')
