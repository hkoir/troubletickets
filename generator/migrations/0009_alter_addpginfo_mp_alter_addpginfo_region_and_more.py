# Generated by Django 5.0.4 on 2024-08-14 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0008_alter_addpginfo_region_alter_addpginfo_zone_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addpginfo',
            name='mp',
            field=models.CharField(blank=True, choices=[('all', 'all'), ('Sylhet', 'Sylhet'), ('Taherpur', 'Taherpur'), ('Sunamganj', 'Sunamganj'), ('Bianibazar', 'Bianaibazar'), ('Dorbhost', 'Dorbhost'), ('Dherai', 'Dherai'), ('Chatak', 'Chatak'), ('Moulovibazar', 'Moulovibazar'), ('Baniachong', 'Baniachong'), ('Juri', 'Juri'), ('Saestaganj', 'Saestaganj'), ('Mymensingh', 'Mymensingh'), ('Fulpur', 'Fulpur'), ('Valuka', 'Valuka'), ('Kisorganj', 'Kisorganj'), ('Netrokona', 'Netrokona'), ('Katiadi', 'Katiadi'), ('Mohonganj', 'Mohonganj'), ('Austogram', 'Austogram'), ('Tangail', 'Tangail'), ('Madhupur', 'Madhupur'), ('Jamalpur', 'Jamalpur'), ('Sherpur', 'Sherpur'), ('Bakshiganj', 'Bakshiganj'), ('Rangpur', 'Rangpur'), ('Hatibandha', 'Hatibandha'), ('Gaibandha', 'Gaibandha'), ('Ulipur', 'Ulipur'), ('Boropar', 'Boropar'), ('Polasbari', 'Polasbari'), ('Dinajpur', 'Dinajpur'), ('Panchghor', 'Panchghor'), ('Jaldhaka', 'Jaldhaka'), ('Thakurgaon', 'Thakurgaon'), ('Rajshahi', 'Rajshahi'), ('Bagura', 'Bagurar'), ('Nachole', 'Nachole'), ('Natore', 'Natore'), ('Chapai', 'Chapai'), ('Bagura', 'Bagura')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='addpginfo',
            name='region',
            field=models.CharField(blank=True, choices=[('all', 'all'), ('Sylhet', 'Sylhet'), ('Rangpur', 'Rangpur')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='addpginfo',
            name='zone',
            field=models.CharField(blank=True, choices=[('all', 'all'), ('Sylhet', 'Sylhet'), ('Moulovibazar', 'Moulovibazar'), ('Mymensingh', 'Mymensingh'), ('Kisorganj', 'Kisorganj'), ('Tangail', 'Tangail'), ('Rangpur', 'Rangpur'), ('Dinajpur', 'Dinajpur'), ('Bagura', 'Bagura'), ('Rajshahi', 'Rajshahi')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='pgfaultrecord',
            name='mp',
            field=models.CharField(blank=True, choices=[('all', 'all'), ('Sylhet', 'Sylhet'), ('Taherpur', 'Taherpur'), ('Sunamganj', 'Sunamganj'), ('Bianibazar', 'Bianaibazar'), ('Dorbhost', 'Dorbhost'), ('Dherai', 'Dherai'), ('Chatak', 'Chatak'), ('Moulovibazar', 'Moulovibazar'), ('Baniachong', 'Baniachong'), ('Juri', 'Juri'), ('Saestaganj', 'Saestaganj'), ('Mymensingh', 'Mymensingh'), ('Fulpur', 'Fulpur'), ('Valuka', 'Valuka'), ('Kisorganj', 'Kisorganj'), ('Netrokona', 'Netrokona'), ('Katiadi', 'Katiadi'), ('Mohonganj', 'Mohonganj'), ('Austogram', 'Austogram'), ('Tangail', 'Tangail'), ('Madhupur', 'Madhupur'), ('Jamalpur', 'Jamalpur'), ('Sherpur', 'Sherpur'), ('Bakshiganj', 'Bakshiganj'), ('Rangpur', 'Rangpur'), ('Hatibandha', 'Hatibandha'), ('Gaibandha', 'Gaibandha'), ('Ulipur', 'Ulipur'), ('Boropar', 'Boropar'), ('Polasbari', 'Polasbari'), ('Dinajpur', 'Dinajpur'), ('Panchghor', 'Panchghor'), ('Jaldhaka', 'Jaldhaka'), ('Thakurgaon', 'Thakurgaon'), ('Rajshahi', 'Rajshahi'), ('Bagura', 'Bagurar'), ('Nachole', 'Nachole'), ('Natore', 'Natore'), ('Chapai', 'Chapai'), ('Bagura', 'Bagura')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='pgfaultrecord',
            name='region',
            field=models.CharField(blank=True, choices=[('all', 'all'), ('Sylhet', 'Sylhet'), ('Rangpur', 'Rangpur')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='pgfaultrecord',
            name='zone',
            field=models.CharField(blank=True, choices=[('all', 'all'), ('Sylhet', 'Sylhet'), ('Moulovibazar', 'Moulovibazar'), ('Mymensingh', 'Mymensingh'), ('Kisorganj', 'Kisorganj'), ('Tangail', 'Tangail'), ('Rangpur', 'Rangpur'), ('Dinajpur', 'Dinajpur'), ('Bagura', 'Bagura'), ('Rajshahi', 'Rajshahi')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='pgfuelrefill',
            name='mp',
            field=models.CharField(blank=True, choices=[('all', 'all'), ('Sylhet', 'Sylhet'), ('Taherpur', 'Taherpur'), ('Sunamganj', 'Sunamganj'), ('Bianibazar', 'Bianaibazar'), ('Dorbhost', 'Dorbhost'), ('Dherai', 'Dherai'), ('Chatak', 'Chatak'), ('Moulovibazar', 'Moulovibazar'), ('Baniachong', 'Baniachong'), ('Juri', 'Juri'), ('Saestaganj', 'Saestaganj'), ('Mymensingh', 'Mymensingh'), ('Fulpur', 'Fulpur'), ('Valuka', 'Valuka'), ('Kisorganj', 'Kisorganj'), ('Netrokona', 'Netrokona'), ('Katiadi', 'Katiadi'), ('Mohonganj', 'Mohonganj'), ('Austogram', 'Austogram'), ('Tangail', 'Tangail'), ('Madhupur', 'Madhupur'), ('Jamalpur', 'Jamalpur'), ('Sherpur', 'Sherpur'), ('Bakshiganj', 'Bakshiganj'), ('Rangpur', 'Rangpur'), ('Hatibandha', 'Hatibandha'), ('Gaibandha', 'Gaibandha'), ('Ulipur', 'Ulipur'), ('Boropar', 'Boropar'), ('Polasbari', 'Polasbari'), ('Dinajpur', 'Dinajpur'), ('Panchghor', 'Panchghor'), ('Jaldhaka', 'Jaldhaka'), ('Thakurgaon', 'Thakurgaon'), ('Rajshahi', 'Rajshahi'), ('Bagura', 'Bagurar'), ('Nachole', 'Nachole'), ('Natore', 'Natore'), ('Chapai', 'Chapai'), ('Bagura', 'Bagura')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='pgfuelrefill',
            name='region',
            field=models.CharField(blank=True, choices=[('all', 'all'), ('Sylhet', 'Sylhet'), ('Rangpur', 'Rangpur')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='pgfuelrefill',
            name='zone',
            field=models.CharField(blank=True, choices=[('all', 'all'), ('Sylhet', 'Sylhet'), ('Moulovibazar', 'Moulovibazar'), ('Mymensingh', 'Mymensingh'), ('Kisorganj', 'Kisorganj'), ('Tangail', 'Tangail'), ('Rangpur', 'Rangpur'), ('Dinajpur', 'Dinajpur'), ('Bagura', 'Bagura'), ('Rajshahi', 'Rajshahi')], max_length=100, null=True),
        ),
    ]
