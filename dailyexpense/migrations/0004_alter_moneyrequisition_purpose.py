# Generated by Django 5.0.4 on 2024-08-13 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dailyexpense', '0003_alter_moneyrequisition_purpose'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moneyrequisition',
            name='purpose',
            field=models.CharField(blank=True, choices=[('Operations', 'Operations'), ('Adhoc_man', 'Adhoc_man'), ('Adhoc_man', 'Adhoc_man')], default='None', max_length=100, null=True),
        ),
    ]
