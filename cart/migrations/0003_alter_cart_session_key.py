# Un carrito cerrado conserva su session_key; por eso no puede ser única.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_cart_session_key_and_design'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='session_key',
            field=models.CharField(
                blank=True, db_index=True, max_length=40, null=True,
                verbose_name='Clave de sesión',
            ),
        ),
    ]
