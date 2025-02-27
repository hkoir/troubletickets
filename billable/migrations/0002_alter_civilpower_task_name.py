# Generated by Django 5.0.4 on 2024-07-16 15:59

import multiselectfield.db.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billable', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='civilpower',
            name='task_name',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('single_phase_meter_change', 'single_phase_meter_change'), ('three_phase_meter_change', 'three_phase_meter_change'), ('5kva_transformer_change', '5kva_transformer_change'), ('10kva_transformer_change', '10kva_transformer_change'), ('transformer_protection', 'transformer_protection'), ('DG_repiar', 'DG_repair')], max_length=132, null=True),
        ),
    ]
