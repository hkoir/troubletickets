# Generated by Django 5.0.4 on 2024-06-19 17:03

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_code', models.CharField(blank=True, default='None', max_length=100, null=True, unique=True)),
                ('name', models.CharField(blank=True, default='Nome', max_length=100, null=True)),
                ('first_name', models.CharField(blank=True, default='Nome', max_length=100, null=True)),
                ('last_name', models.CharField(blank=True, default='Nome', max_length=100, null=True)),
                ('posting_area', models.CharField(blank=True, choices=[('Dhaka', 'Dhaka'), ('Rangpur', 'Rangpur'), ('Sylhet', 'Sylhet'), ('Rajshahi', 'Rajshahi'), ('Chittagong', 'Chittagong')], max_length=100, null=True)),
                ('gender', models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')], default='Nome', max_length=20, null=True)),
                ('address', models.TextField(blank=True, default='None', null=True)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(blank=True, default='Nome', max_length=15, null=True)),
                ('joining_date', models.DateField()),
                ('resignation_date', models.DateField(blank=True, default=django.utils.timezone.now, help_text='Format: YYYY-MM-DD', null=True)),
                ('position', models.CharField(blank=True, choices=[('Chairman', 'Chairman'), ('MD', 'MD'), ('CEO', 'CEO'), ('CFO', 'CFO'), ('CMO', 'CMO'), ('CTO', 'CTO'), ('Specialist', 'Specialist'), ('Manager', 'Manager'), ('Sr.Manager', 'Sr.Manager'), ('DGM', 'DGM'), ('GM', 'GM'), ('SrGM', 'SrGM'), ('Director', 'Director'), ('HOD', 'HOD'), ('Specialist', 'Specialist'), ('HSS_manager', 'HSS_manager'), ('Driver', 'Driver'), ('Peon', 'Peon'), ('General staff', 'General staff')], default='Nome', max_length=100, null=True)),
                ('department', models.CharField(blank=True, choices=[('Engineering', 'Engineering'), ('Marketting', 'Marketing'), ('Finance', 'Finance'), ('Accounting', 'Accounting'), ('Technology', 'Technology'), ('Admin', 'Admin'), ('HR', 'HR'), ('Business_Development', 'Business_Development')], default='Nome', max_length=100, null=True)),
                ('employe_level', models.CharField(choices=[('SeniorManagement', 'SeniorManagement'), ('MidLevelManager', 'MidLevelManager'), ('FirstLevelmanager', 'FirstLevelManager'), ('Executive', 'Executive'), ('Engineer', 'Engineer'), ('Doctor', 'Doctor'), ('Specialist', 'Specialist'), ('Officer', 'Officer'), ('FieldForce', 'FieldForce'), ('General_Staffs', 'General_Staffs')], default='executive', max_length=100)),
                ('basic_salary', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('house_allowance', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('medical_allowance', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('transportation_allowance', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('bonus', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('overtime_pay_rate', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pictures/')),
                ('gross_monthly_salary', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(blank=True, choices=[('Sylhet', 'Sylhet'), ('Rangpur', 'Rangpur')], max_length=100, null=True)),
                ('zone', models.CharField(blank=True, choices=[('Sylhet', 'Sylhet'), ('Taherpur', 'Taherpur'), ('Sunamganj', 'Sunamganj'), ('Bianibazar', 'Bianaibazar'), ('Dorbhost', 'Dorbhost'), ('Dherai', 'Dherai'), ('Chatak', 'Chatak'), ('Moulovibazar', 'Moulovibazar'), ('Baniachong', 'Baniachong'), ('Juri', 'Juri'), ('Saestaganj', 'Saestaganj'), ('Mymensingh', 'Mymensingh'), ('Fulpur', 'Fulpur'), ('Valuka', 'Valuka'), ('Kisorganj', 'Kisorganj'), ('Netrokona', 'Netrokona'), ('Katiadi', 'Katiadi'), ('Mohonganj', 'Mohonganj'), ('Austogram', 'Austogram'), ('Tangail', 'Tangail'), ('Madhupur', 'Madhupur'), ('Jamalpur', 'Jamalpur'), ('Sherpur', 'Sherpur'), ('Bakshiganj', 'Bakshiganj'), ('Rangpur', 'Rangpur'), ('Hatibandha', 'Hatibandha'), ('Gaibandha', 'Gaibandha'), ('Ulipur', 'Ulipur'), ('Boropar', 'Boropar'), ('Polasbari', 'Polasbari'), ('Dinajpur', 'Dinajpur'), ('Panchghor', 'Panchghor'), ('Jaldhaka', 'Jaldhaka'), ('Thakurgaon', 'Thakurgaon'), ('Rajshahi', 'Rajshahi'), ('Bagura', 'Bagurar'), ('Nachole', 'Nachole'), ('Natore', 'Natore'), ('Chapai', 'Chapai'), ('Bagura', 'Bagura')], max_length=100, null=True)),
                ('mp', models.CharField(blank=True, choices=[('Sylhet', 'Sylhet'), ('Rangpur', 'Rangpur')], max_length=100, null=True)),
                ('total_site', models.IntegerField(blank=True, null=True)),
                ('no_of_KPI_site', models.IntegerField(blank=True, null=True)),
                ('num_of_PGTL', models.IntegerField(blank=True, null=True)),
                ('num_of_PGR', models.IntegerField(blank=True, null=True)),
                ('num_of_adhoc_PGR', models.IntegerField(blank=True, null=True)),
                ('num_of_vehicle', models.IntegerField(blank=True, null=True)),
                ('num_of_good_PG', models.IntegerField(blank=True, null=True)),
                ('num_of_faulty_PG', models.IntegerField(blank=True, null=True)),
                ('num_of_adhoc_vehicle', models.IntegerField(blank=True, null=True)),
                ('num_of_PG_repair_technician', models.IntegerField(blank=True, null=True)),
                ('num_of_DG_repair_technician', models.IntegerField(blank=True, null=True)),
                ('num_of_operational_executive', models.IntegerField(blank=True, null=True)),
                ('num_of_admin_account_executive', models.IntegerField(blank=True, null=True)),
                ('num_of_manager', models.IntegerField(blank=True, null=True)),
                ('num_of_other_staff', models.IntegerField(blank=True, null=True)),
                ('total_human_resource', models.IntegerField(blank=True, null=True)),
                ('faulty_PG_percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='AttendanceModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('check_in_time', models.TimeField()),
                ('check_out_time', models.TimeField(blank=True, null=True)),
                ('total_hours', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=5, null=True)),
                ('attendance_status', models.CharField(choices=[('present', 'present'), ('absent', 'absent')], default='None', max_length=50)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee.employeemodel')),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeRecordChange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('field_name', models.CharField(default='None', max_length=100)),
                ('old_value', models.CharField(default='None', max_length=255)),
                ('new_value', models.CharField(default='None', max_length=255)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee.employeemodel')),
            ],
        ),
        migrations.CreateModel(
            name='MonthlySalaryReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.IntegerField()),
                ('year', models.IntegerField()),
                ('total_working_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('total_salary', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee.employeemodel')),
            ],
        ),
    ]
