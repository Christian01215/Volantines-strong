from django.db import models
from django.conf import settings
# Product reference used as string

class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False, verbose_name="Finalizada")
    
    def __str__(self):
        return f"Carrito #{self.pk}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    price_at_time = models.IntegerField(verbose_name="Precio al momento")  # snapshot
    
    class Meta:
        verbose_name = "Elemento de carrito"
        verbose_name_plural = "Elementos de carrito"
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    @property
    def line_total(self):
        return self.price_at_time * self.quantity
