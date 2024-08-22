# Generated by Django 5.0.4 on 2024-07-09 17:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adhocman', '0019_alter_adhocattendance_adhoc_working_hours_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adhocattendance',
            name='adhoc_payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='adhoc_man_payment_ref', to='adhocman.adhocpayment'),
        ),
        migrations.AlterField(
            model_name='adhocattendance',
            name='adhoc_requisition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='adhoc_man_requisition_ref', to='adhocman.adhocrequisition'),
        ),
    ]
