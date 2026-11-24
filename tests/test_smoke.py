"""Pruebas smoke: todas las rutas públicas renderizan sin TemplateDoesNotExist."""
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product, ProductImage


class PublicUrlsSmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Volantines", slug="volantines")
        cls.product = Product.objects.create(
            name="Volantín prueba",
            slug="volantin-prueba",
            category=cls.category,
            price=10000,
            stock=5,
        )

    def test_health(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_catalog(self):
        response = self.client.get(reverse("products:catalog"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Volantín prueba")
        self.assertContains(
            response, 'rel="icon" type="image/png" href="/static/favicon.png"'
        )

    def test_product_detail(self):
        response = self.client.get(reverse("products:detail", args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Volantín prueba")
        self.assertContains(response, "gallery-stage")

    def test_catalog_card_exposes_gallery_for_modal(self):
        ProductImage.objects.create(
            product=self.product,
            image_url="https://res.cloudinary.com/demo/image/upload/gallery-1.jpg",
            order=0,
        )
        response = self.client.get(reverse("products:catalog"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-gallery=")
        self.assertContains(response, "gallery-1.jpg")
        self.assertContains(response, "gallery-stage")

    def test_cart_pages(self):
        self.assertEqual(self.client.get(reverse("cart:view")).status_code, 200)
        self.assertEqual(self.client.get(reverse("cart:checkout")).status_code, 302)

        self.client.post(
            reverse("cart:api_add"),
            {"product_id": self.product.pk, "quantity": 1},
        )
        self.assertEqual(self.client.get(reverse("cart:checkout")).status_code, 200)

    def test_cart_api(self):
        response = self.client.get(reverse("cart:api"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 0)

        response = self.client.post(
            reverse("cart:api_add"),
            {"product_id": self.product.pk, "quantity": 2},
        )
        self.assertEqual(response.json()["count"], 2)

        response = self.client.post(
            reverse("cart:api_update"),
            {"product_id": self.product.pk, "quantity": 4},
        )
        self.assertEqual(response.json()["count"], 4)

        response = self.client.post(
            reverse("cart:api_remove"),
            {"product_id": self.product.pk},
        )
        self.assertEqual(response.json()["count"], 0)
