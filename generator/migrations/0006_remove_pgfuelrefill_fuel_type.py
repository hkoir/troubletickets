# Generated by Django 5.0.4 on 2024-07-02 05:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0005_alter_pgfuelrefill_fuel_pump'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pgfuelrefill',
            name='fuel_type',
        ),
    ]
