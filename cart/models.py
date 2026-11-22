from django.db import models


class Cart(models.Model):
    """Carrito persistido en base de datos, asociado a la sesión del comprador."""

    session_key = models.CharField(
        max_length=40,
        db_index=True,
        blank=True,
        null=True,
        verbose_name="Clave de sesión",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False, verbose_name="Finalizada")

    class Meta:
        verbose_name = "Carrito"
        verbose_name_plural = "Carritos"

    def __str__(self):
        return f"Carrito #{self.pk}"

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total(self):
        return sum(item.line_total for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, verbose_name="Producto"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    price_at_time = models.IntegerField(
        verbose_name="Precio al momento"
    )  # snapshot informativo; el checkout siempre recalcula desde Product
    design_url = models.URLField(blank=True, verbose_name="URL del diseño personalizado")
    design_name = models.CharField(
        max_length=255, blank=True, verbose_name="Nombre del diseño"
    )

    class Meta:
        verbose_name = "Elemento de carrito"
        verbose_name_plural = "Elementos de carrito"

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    @property
    def line_total(self):
        return self.price_at_time * self.quantity
