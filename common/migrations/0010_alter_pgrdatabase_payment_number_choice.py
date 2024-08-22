# Generated by Django 5.0.4 on 2024-07-23 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0009_pgrdatabase_payment_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pgrdatabase',
            name='payment_number_choice',
            field=models.CharField(blank=True, choices=[('bikash', 'biksah'), ('nagad', 'nagad'), ('rocket', 'rocket')], default='bikash', max_length=100, null=True),
        ),
    ]
