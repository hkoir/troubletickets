# Generated by Django 5.0.4 on 2024-08-31 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0006_resource_num_of_ac_ibs_resource_num_of_dgow_runner_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='num_of_AZM',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='num_of_RM',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='num_of_ZM',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
