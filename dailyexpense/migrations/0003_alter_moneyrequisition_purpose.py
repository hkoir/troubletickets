# Generated by Django 5.0.4 on 2024-08-11 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dailyexpense', '0002_alter_dailyexpenserequisition_purpose'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moneyrequisition',
            name='purpose',
            field=models.CharField(blank=True, choices=[('Operations', 'Operations'), ('Adhoc_man_vehicle', 'Adhoc_man_vehicle'), ('General', 'General'), ('spare_purchase', 'spare_purchase'), ('others', 'others')], default='None', max_length=100, null=True),
        ),
    ]
