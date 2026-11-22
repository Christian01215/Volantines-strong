from django.db import models
from django.conf import settings
from products.models import Product, Category


ORDER_STATUS_CHOICES = [
    ("pendiente", "Pendiente"),
    ("pago_confirmado", "Pago Confirmado"),
    ("preparando", "Preparando"),
    ("listo_para_retiro", "Listo para Retiro"),
    ("retirado", "Retirado"),
    ("cancelado", "Cancelado"),
]


class Order(models.Model):
    STATUS_CHOICES = ORDER_STATUS_CHOICES
    
    code = models.CharField(max_length=20, unique=True, verbose_name="Código de orden")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")
    
    customer_name = models.CharField(max_length=200, blank=True, verbose_name="Nombre completo")
    customer_rut = models.CharField(max_length=12, blank=True, verbose_name="RUT")
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    customer_email = models.EmailField(blank=True, verbose_name="Correo electrónico")
    
    delivery_type = models.CharField(
        max_length=20,
        choices=[
            ("click_collect", "Retiro en taller (Click & Collect)"),
            ("delivery", "Despacho domicilio"),
        ],
        default="click_collect",
        verbose_name="Tipo de entrega",
    )
    
    pickup_date = models.DateField(blank=True, null=True, verbose_name="Fecha de retiro")
    pickup_slot = models.CharField(max_length=20, blank=True, verbose_name="Bloque horario")
    
    total = models.IntegerField(verbose_name="Total CLP")
    payment_method = models.CharField(max_length=30, blank=True, verbose_name="Medio de pago")

    delivery_region = models.CharField(max_length=100, blank=True, verbose_name="Región")
    delivery_commune = models.CharField(max_length=100, blank=True, verbose_name="Comuna")
    delivery_address = models.TextField(blank=True, verbose_name="Dirección de entrega")

    receipt_url = models.URLField(blank=True, verbose_name="URL del comprobante")
    receipt_name = models.CharField(max_length=255, blank=True, verbose_name="Nombre del comprobante")

    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default="pendiente",
        verbose_name="Estado",
    )
    
    cart = models.OneToOneField(
        "cart.Cart", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="order", verbose_name="Carrito origen"
    )
    
    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ["-" + "created_at"]
    
    def __str__(self):
        return f"Orden {self.code} - {self.get_status_display()}"
    
    @property
    def total_display(self):
        return f"${self.total:,}".replace(",", ".")

    @property
    def is_ready_for_pickup(self):
        return self.status == "listo_para_retiro"
    
    @property
    def is_finalized(self):
        return self.status == "retirado"
    
    def mark_preparing(self):
        self.status = "preparando"
        self.save(update_fields=["status"])
    
    def mark_ready_for_pickup(self):
        self.status = "listo_para_retiro"
        self.save(update_fields=["status"])
    
    def mark_as_retirado(self):
        self.status = "retirado"
        self.save(update_fields=["status"])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    price = models.IntegerField(verbose_name="Precio unitario")
    design_url = models.URLField(blank=True, verbose_name="URL del diseño personalizado")
    design_name = models.CharField(max_length=255, blank=True, verbose_name="Nombre del diseño")

    class Meta:
        verbose_name = "Elemento de orden"
        verbose_name_plural = "Elementos de orden"
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    @property
    def line_total(self):
        return self.price * self.quantity
