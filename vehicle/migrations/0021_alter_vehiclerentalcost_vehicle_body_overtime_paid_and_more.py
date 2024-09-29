# Generated by Django 5.0.4 on 2024-08-31 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0020_alter_vehiclerentalcost_vehicle_body_overtime_paid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehiclerentalcost',
            name='vehicle_body_overtime_paid',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='vehiclerentalcost',
            name='vehicle_driver_overtime_paid',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='vehiclerentalcost',
            name='vehicle_kilometer_paid',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='vehiclerentalcost',
            name='vehicle_rent_paid',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='vehiclerentalcost',
            name='vehicle_total_paid',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
    ]
