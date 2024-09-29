# Generated by Django 5.1.1 on 2024-09-26 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dailyexpense', '0009_alter_dailyexpenserequisition_mp'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyexpenserequisition',
            name='user_type',
            field=models.CharField(choices=[('CM_user', 'CM_user'), ('PM_user', 'PM_user'), ('general_user', 'general_user')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='dailyexpenserequisition',
            name='work_type',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='dailyexpenserequisition',
            name='purpose',
            field=models.CharField(choices=[('local_conveyance', 'local_conveyance'), ('long_distance_transport', 'long_distance_transport'), ('pg_carrying_cost', 'pg_carrying-cost'), ('night_bill', 'night_bill'), ('pg_local_fuel_purchase', 'pg_local_fuel_purchase'), ('vehicle_local_fuel_purchase', 'vehicle_local_fuel_purchase'), ('toll', 'toll'), ('food', 'food'), ('item_purchase', 'item_purchase'), ('field_advance', 'field_advance'), ('DA', 'DA'), ('hotel_bill', 'hotel_bill'), ('others', 'others')], max_length=100),
        ),
    ]
