# Generado para el carrito persistido en base de datos y diseños personalizados.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cart',
            options={'verbose_name': 'Carrito', 'verbose_name_plural': 'Carritos'},
        ),
        migrations.AddField(
            model_name='cart',
            name='session_key',
            field=models.CharField(
                blank=True, max_length=40, null=True, unique=True,
                verbose_name='Clave de sesión',
            ),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='design_name',
            field=models.CharField(blank=True, max_length=255, verbose_name='Nombre del diseño'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='design_url',
            field=models.URLField(blank=True, verbose_name='URL del diseño personalizado'),
        ),
    ]
