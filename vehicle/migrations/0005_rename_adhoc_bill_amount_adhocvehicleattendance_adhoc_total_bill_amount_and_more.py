# Generated by Django 5.0.4 on 2024-07-29 14:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0004_adhocvehicleattendance_vehicle_fault_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='adhocvehicleattendance',
            old_name='adhoc_bill_amount',
            new_name='adhoc_total_bill_amount',
        ),
        migrations.AddField(
            model_name='adhocvehicleattendance',
            name='adhoc_kilometer_run',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='adhocvehicleattendance',
            name='adhoc_vehicle_bill_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='adhocvehicleattendance',
            name='kilometer_cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='adhocvehicleattendance',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehicle_attendance', to='vehicle.addvehicleinfo'),
        ),
        migrations.AlterField(
            model_name='adhocvehicleattendance',
            name='vehicle_fault',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vehicle_fault', to='vehicle.vehiclefault'),
        ),
        migrations.AlterField(
            model_name='adhocvehicleattendance',
            name='vehicle_running_data',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vehicle_running_data', to='vehicle.vehicleruniningdata'),
        ),
    ]
