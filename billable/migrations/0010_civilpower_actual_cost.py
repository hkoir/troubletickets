# Generated by Django 5.0.4 on 2024-07-31 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billable', '0009_chatmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='civilpower',
            name='actual_cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
