# Generated by Django 5.0.4 on 2024-08-11 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0010_alter_pgrdatabase_payment_number_choice'),
    ]

    operations = [
        migrations.AddField(
            model_name='pgrdatabase',
            name='PGR_01hour_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='pgrdatabase',
            name='PGR_12hour_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='pgrdatabase',
            name='PGR_24hour_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
