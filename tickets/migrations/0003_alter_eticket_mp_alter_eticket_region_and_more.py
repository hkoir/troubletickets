# Generated by Django 5.0.4 on 2024-07-22 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_eticket_ticket_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eticket',
            name='mp',
            field=models.CharField(blank=True, choices=[('Sylhet', 'Sylhet'), ('Taherpur', 'Taherpur'), ('Sunamganj', 'Sunamganj'), ('Bianibazar', 'Bianaibazar'), ('Dorbhost', 'Dorbhost'), ('Dherai', 'Dherai'), ('Chatak', 'Chatak'), ('Moulovibazar', 'Moulovibazar'), ('Baniachong', 'Baniachong'), ('Juri', 'Juri'), ('Saestaganj', 'Saestaganj'), ('Mymensingh', 'Mymensingh'), ('Fulpur', 'Fulpur'), ('Valuka', 'Valuka'), ('Kisorganj', 'Kisorganj'), ('Netrokona', 'Netrokona'), ('Katiadi', 'Katiadi'), ('Mohonganj', 'Mohonganj'), ('Austogram', 'Austogram'), ('Tangail', 'Tangail'), ('Madhupur', 'Madhupur'), ('Jamalpur', 'Jamalpur'), ('Sherpur', 'Sherpur'), ('Bakshiganj', 'Bakshiganj'), ('Rangpur', 'Rangpur'), ('Hatibandha', 'Hatibandha'), ('Gaibandha', 'Gaibandha'), ('Ulipur', 'Ulipur'), ('Boropar', 'Boropar'), ('Polasbari', 'Polasbari'), ('Dinajpur', 'Dinajpur'), ('Panchghor', 'Panchghor'), ('Jaldhaka', 'Jaldhaka'), ('Thakurgaon', 'Thakurgaon'), ('Rajshahi', 'Rajshahi'), ('Bagura', 'Bagurar'), ('Nachole', 'Nachole'), ('Natore', 'Natore'), ('Chapai', 'Chapai'), ('Bagura', 'Bagura')], default=None, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='eticket',
            name='region',
            field=models.CharField(blank=True, choices=[('Sylhet', 'Sylhet'), ('Rangpur', 'Rangpur')], default=None, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='eticket',
            name='zone',
            field=models.CharField(blank=True, choices=[('Sylhet', 'Sylhet'), ('Moulovibazar', 'Moulovibazar'), ('Mymensingh', 'Mymensingh'), ('Kisorganj', 'Kisorganj'), ('Tangail', 'Tangail'), ('Rangpur', 'Rangpur'), ('Dinajpur', 'Dinajpur'), ('Bagura', 'Bagura'), ('Rajshahi', 'Rajshahi')], default=None, max_length=100, null=True),
        ),
    ]
