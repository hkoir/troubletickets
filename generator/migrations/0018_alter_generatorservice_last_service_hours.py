# Generated by Django 5.0.4 on 2024-08-24 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0017_alter_generatorservice_last_service_hours'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generatorservice',
            name='last_service_hours',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
