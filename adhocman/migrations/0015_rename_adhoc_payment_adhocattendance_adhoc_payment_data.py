# Generated by Django 5.0.4 on 2024-06-27 04:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adhocman', '0014_alter_adhocattendance_adhoc_payment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='adhocattendance',
            old_name='adhoc_payment',
            new_name='adhoc_payment_data',
        ),
    ]
