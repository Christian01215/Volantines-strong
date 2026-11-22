from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    description = models.TextField(blank=True, verbose_name="Descripción")
    image = models.ImageField(upload_to="categories/", blank=True, null=True, verbose_name="Imagen")
    order = models.IntegerField(default=0, verbose_name="Orden")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", verbose_name="Categoría")
    price = models.IntegerField(verbose_name="Precio CLP")
    cost = models.IntegerField(default=0, verbose_name="Costo CLP")
    stock = models.IntegerField(default=0, verbose_name="Stock")
    specs = models.TextField(blank=True, verbose_name="Ficha técnica")
    description = models.TextField(blank=True, verbose_name="Descripción")
    image = models.ImageField(upload_to="products/", blank=True, null=True, verbose_name="Imagen principal")
    image_url = models.URLField(blank=True, verbose_name="URL remota de la imagen")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")

    class Meta:
        ordering = ["name"]
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.name} - {self.category.name}"

    @property
    def formatted_price(self):
        return f"${self.price:,.0f} CLP"

    @property
    def price_display(self):
        """Precio en formato chileno para la grilla del catálogo."""
        return f"${self.price:,}".replace(",", ".")


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery", verbose_name="Producto")
    image = models.ImageField(upload_to="products/gallery/", blank=True, null=True, verbose_name="Imagen")
    image_url = models.URLField(blank=True, verbose_name="URL remota de la imagen")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")

    class Meta:
        ordering = ["order", "pk"]
        verbose_name = "Imagen de galería"
        verbose_name_plural = "Imágenes de galería"

    def __str__(self):
        return f"{self.product.name} — imagen {self.order + 1}"
