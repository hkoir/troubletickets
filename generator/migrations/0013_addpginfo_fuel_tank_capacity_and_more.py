# Generated by Django 5.0.4 on 2024-08-24 10:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0012_alter_pgfuelrefill_refill_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='addpginfo',
            name='fuel_tank_capacity',
            field=models.CharField(choices=[('5kva', '5kva'), ('6kva', '6kva'), ('8kva', '8kva'), ('30kva', '30kva'), ('40kva', '40kva')], default='None', max_length=50),
        ),
        migrations.AddField(
            model_name='addpginfo',
            name='lub_oil_capacity',
            field=models.CharField(choices=[('5kva', '5kva'), ('6kva', '6kva'), ('8kva', '8kva'), ('30kva', '30kva'), ('40kva', '40kva')], default='None', max_length=50),
        ),
        migrations.AlterField(
            model_name='addpginfo',
            name='PG_brand',
            field=models.CharField(choices=[('Honda', 'Honda'), ('Mistsubishi', 'Mistsubishi'), ('wilson', 'wilson'), ('chinese', 'chinese'), ('mahindrea', 'mahindra')], default='None', max_length=50),
        ),
        migrations.AlterField(
            model_name='addpginfo',
            name='PG_capacity',
            field=models.CharField(choices=[('5kva', '5kva'), ('6kva', '6kva'), ('8kva', '8kva'), ('30kva', '30kva'), ('40kva', '40kva')], default='None', max_length=50),
        ),
        migrations.AlterField(
            model_name='addpginfo',
            name='PG_deployment_type',
            field=models.CharField(blank=True, choices=[('movable_PG', 'movable_PG'), ('fixed_PG', 'fixed_PG'), ('fixed_DG', 'fixed_DG')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='addpginfo',
            name='PG_supplier',
            field=models.CharField(choices=[('vendor1', 'vendor1'), ('vendor2', 'vendor2'), ('vendor3', 'vendor3'), ('own', 'own'), ('edotco', 'edotco')], default='None', max_length=50),
        ),
        migrations.CreateModel(
            name='GeneratorService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(blank=True, choices=[('', ''), ('Sylhet', 'Sylhet'), ('Rangpur', 'Rangpur')], max_length=100, null=True)),
                ('zone', models.CharField(blank=True, choices=[('', ''), ('Sylhet', 'Sylhet'), ('Moulovibazar', 'Moulovibazar'), ('Mymensingh', 'Mymensingh'), ('Kisorganj', 'Kisorganj'), ('Tangail', 'Tangail'), ('Rangpur', 'Rangpur'), ('Dinajpur', 'Dinajpur'), ('Bagura', 'Bagura'), ('Rajshahi', 'Rajshahi')], max_length=100, null=True)),
                ('mp', models.CharField(blank=True, choices=[('', ''), ('Sylhet', 'Sylhet'), ('Taherpur', 'Taherpur'), ('Sunamganj', 'Sunamganj'), ('Bianibazar', 'Bianaibazar'), ('Dorbhost', 'Dorbhost'), ('Dherai', 'Dherai'), ('Chatak', 'Chatak'), ('Moulovibazar', 'Moulovibazar'), ('Baniachong', 'Baniachong'), ('Juri', 'Juri'), ('Saestaganj', 'Saestaganj'), ('Mymensingh', 'Mymensingh'), ('Fulpur', 'Fulpur'), ('Valuka', 'Valuka'), ('Kisorganj', 'Kisorganj'), ('Netrokona', 'Netrokona'), ('Katiadi', 'Katiadi'), ('Mohonganj', 'Mohonganj'), ('Austogram', 'Austogram'), ('Tangail', 'Tangail'), ('Madhupur', 'Madhupur'), ('Jamalpur', 'Jamalpur'), ('Sherpur', 'Sherpur'), ('Bakshiganj', 'Bakshiganj'), ('Rangpur', 'Rangpur'), ('Hatibandha', 'Hatibandha'), ('Gaibandha', 'Gaibandha'), ('Ulipur', 'Ulipur'), ('Boropar', 'Boropar'), ('Polasbari', 'Polasbari'), ('Dinajpur', 'Dinajpur'), ('Panchghor', 'Panchghor'), ('Jaldhaka', 'Jaldhaka'), ('Thakurgaon', 'Thakurgaon'), ('Rajshahi', 'Rajshahi'), ('Bagura', 'Bagurar'), ('Nachole', 'Nachole'), ('Natore', 'Natore'), ('Chapai', 'Chapai'), ('Bagura', 'Bagura')], max_length=100, null=True)),
                ('date_of_service', models.DateField(blank=True, null=True)),
                ('total_run_hour_passed', models.FloatField(blank=True, null=True)),
                ('total_days_passed', models.FloatField(blank=True, null=True)),
                ('created_at', models.DateField(blank=True, null=True)),
                ('pgnumber', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gen_service', to='generator.addpginfo')),
            ],
        ),
    ]
