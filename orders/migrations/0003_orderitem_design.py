# Generado para asociar el diseño personalizado a cada línea del pedido.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_delivery_address_order_delivery_commune_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='design_name',
            field=models.CharField(blank=True, max_length=255, verbose_name='Nombre del diseño'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='design_url',
            field=models.URLField(blank=True, verbose_name='URL del diseño personalizado'),
        ),
    ]
