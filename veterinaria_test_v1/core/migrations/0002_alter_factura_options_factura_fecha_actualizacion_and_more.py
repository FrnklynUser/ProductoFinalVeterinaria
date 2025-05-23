# Generated by Django 5.2.1 on 2025-05-24 04:29

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='factura',
            options={'ordering': ['-fecha_emision'], 'verbose_name': 'Factura', 'verbose_name_plural': 'Facturas'},
        ),
        migrations.AddField(
            model_name='factura',
            name='fecha_actualizacion',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='factura',
            name='cita',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='facturas', to='core.cita'),
        ),
        migrations.AlterField(
            model_name='factura',
            name='iva',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='factura',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
        migrations.AlterField(
            model_name='factura',
            name='total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
