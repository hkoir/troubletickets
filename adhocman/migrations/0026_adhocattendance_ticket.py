# Generated by Django 5.0.4 on 2024-07-25 17:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adhocman', '0025_remove_adhocattendance_adhoc_net_payment'),
        ('tickets', '0003_alter_eticket_mp_alter_eticket_region_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='adhocattendance',
            name='ticket',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tickets.eticket'),
        ),
    ]
