# Generated by Django 5.0.4 on 2024-08-22 05:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0017_remove_pgrdatabase_pgr_contact_hour_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pgrdatabase',
            name='PGR_salary',
        ),
    ]
