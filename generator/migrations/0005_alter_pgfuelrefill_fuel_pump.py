# Generated by Django 5.0.4 on 2024-06-20 13:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_fuelpumpdatabase_fuel_unit_price'),
        ('generator', '0004_alter_pgfuelrefill_refill_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pgfuelrefill',
            name='fuel_pump',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pump_data_info', to='common.fuelpumpdatabase'),
        ),
    ]
