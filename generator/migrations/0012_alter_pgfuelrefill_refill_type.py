# Generated by Django 5.0.4 on 2024-08-18 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0011_alter_addpginfo_mp_alter_pgfaultrecord_mp_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pgfuelrefill',
            name='refill_type',
            field=models.CharField(blank=True, choices=[('pump', 'pump'), ('local_purchase', 'local_purchase')], default=None, max_length=20, null=True),
        ),
    ]
