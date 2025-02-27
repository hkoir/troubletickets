# Generated by Django 5.0.4 on 2024-07-17 13:24

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billable', '0004_rename_task_tt_number_civilpower_tt_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='civilpower',
            name='payment_document_image',
        ),
        migrations.AddField(
            model_name='civilpower',
            name='money_sending_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AddField(
            model_name='civilpower',
            name='receiving_status',
            field=models.CharField(blank=True, default='None', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='civilpower',
            name='sending_document',
            field=models.FileField(blank=True, null=True, upload_to='Civil_power_Money_sending_documents/'),
        ),
    ]
