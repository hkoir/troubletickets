# Generated by Django 5.0.4 on 2024-07-09 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adhocman', '0020_alter_adhocattendance_adhoc_payment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adhocpayment',
            name='payment_supporting_document',
            field=models.ImageField(blank=True, null=True, upload_to='adhoc_man_payment'),
        ),
    ]
