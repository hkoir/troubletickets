from django.db import models
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
# from account.models import Customer
from decimal import Decimal, ROUND_DOWN

from common.models import PGRdatabase,PGTLdatabase

from vehicle.models import AddVehicleInfo
from generator.models import AddPGInfo
from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES



class EmployeeModel(models.Model): 
    employee_code = models.CharField(max_length=100, unique=True, null=True, blank=True, default='None')
    name = models.CharField(max_length=100, null=True, blank=True,default="Nome")
    first_name = models.CharField(max_length=100, null=True, blank=True,default="Nome")
    last_name = models.CharField(max_length=100,null=True, blank=True,default="Nome")
    posting_area_choices=[
        ('Dhaka','Dhaka'),
        ('Rangpur','Rangpur'),
        ('Sylhet','Sylhet'),
        ('Rajshahi','Rajshahi'),
        ('Chittagong','Chittagong')
    ]
    posting_area = models.CharField(max_length=100,choices=posting_area_choices,null=True,blank=True)

    gender_choices =[
        ('Male','Male'),
        ('Female','Female'),
        ('Others', 'Others')
    ]
    gender = models.CharField(max_length=20,choices= gender_choices,null=True, blank=True,default="Nome")
    address=models.TextField(null=True, blank=True,default="None")
    email = models.EmailField()
    phone_number = models.CharField(max_length=15,null=True, blank=True,default="Nome")
    joining_date = models.DateField()
    resignation_date = models.DateField(null=True, blank=True, default=timezone.now, help_text="Format: YYYY-MM-DD")

    position_choices=[

        ('Chairman','Chairman'),
        ('MD','MD'),
        ('CEO','CEO'),
        ('CFO','CFO'),
        ('CMO','CMO'),
        ('CTO','CTO'),
        ('Specialist','Specialist'),
        ('Manager','Manager'),
        ('Sr.Manager','Sr.Manager'),
        ('DGM','DGM'),
        ('GM','GM'),
        ('SrGM','SrGM'),
        ('Director','Director'),
        ('HOD','HOD'),
        ('Specialist','Specialist'),

        ('HSS_manager','HSS_manager'),
        ('Driver','Driver'),
        ('Peon','Peon'),
        ('General staff','General staff'),
     

        
    ]
    position = models.CharField(max_length=100,null=True, blank=True,choices= position_choices,default="Nome")

    department_choices=[

        ('Engineering','Engineering'),
        ('Marketting','Marketing'),
        ('Finance','Finance'),
        ('Accounting','Accounting'),
        ('Technology','Technology'),
        ('Admin','Admin'),
        ('HR','HR'),
        ('Business_Development','Business_Development'),
        
    ]
    department = models.CharField(max_length=100,null=True, blank=True,choices=department_choices,default="Nome")
    
    
    employee_level_choices=[
        ('SeniorManagement','SeniorManagement'),
        ('MidLevelManager','MidLevelManager'),
        ('FirstLevelmanager','FirstLevelManager'),
        ('Executive','Executive'),
        ('Engineer','Engineer'),
        ('Doctor','Doctor'),
        ('Specialist','Specialist'),
        ('Officer','Officer'),
        ('FieldForce','FieldForce'),
        ('General_Staffs','General_Staffs'),
    ]
    employe_level= models.CharField(max_length=100, choices=employee_level_choices, default='executive')
   
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True,default=0.00)
    house_allowance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,default=0.00)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, default=0.00)
    transportation_allowance = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, default=0.00)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    overtime_pay_rate = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, default=0.00)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    gross_monthly_salary = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, default=0.00)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):

        percentage_40 = Decimal('0.4')
        percentage_30 = Decimal('0.3')
        self.house_allowance = self.basic_salary * percentage_40
        self.medical_allowance = self.basic_salary * percentage_40
        self.transportation_allowance = self.basic_salary * percentage_30
        self.bonus = self.basic_salary * percentage_40
        self. gross_monthly_salary = self.basic_salary + self.house_allowance + self.medical_allowance + self.transportation_allowance
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name



class EmployeeRecordChange(models.Model):
    employee = models.ForeignKey(EmployeeModel, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(default=timezone.now)
    field_name = models.CharField(max_length=100,default="None")
    old_value = models.CharField(max_length=255, default="None")
    new_value = models.CharField(max_length=255,default="None" )



class AttendanceModel(models.Model):
    employee = models.ForeignKey(EmployeeModel, on_delete=models.CASCADE)
    date = models.DateField()
    check_in_time = models.TimeField()
    check_out_time = models.TimeField(null=True, blank=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    
    attendance_status_choices=[
        ('present', 'present'),
        ('absent', 'absent'),

    ]
    attendance_status= models.CharField(max_length=50,choices= attendance_status_choices,default='None')
   
    def calculate_total_hours(self):
        if self.check_out_time and self.check_in_time:
            check_in = datetime.combine(datetime.min, self.check_in_time)
            check_out = datetime.combine(datetime.min, self.check_out_time)
            duration = check_out - check_in
            total_hours = duration.total_seconds() / 3600  # Convert seconds to hours
            return round(total_hours, 2)
        else:
            return 0.0  # Return 0.0 if either check_in_time or check_out_time is None

    def save(self, *args, **kwargs):
        self.total_hours = self.calculate_total_hours()
        super().save(*args, **kwargs)
   

    def __str__(self):
        return f"{self.employee} - {self.date}"
    



class MonthlySalaryReport(models.Model):
    employee = models.ForeignKey(EmployeeModel, on_delete=models.CASCADE)
    month = models.IntegerField()  # Month number (e.g., 1 for January)
    year = models.IntegerField()
    total_working_hours = models.DecimalField(max_digits=5, decimal_places=2 , null=True, blank=True )
    total_salary = models.DecimalField(max_digits=10, decimal_places=2 , null=True, blank=True)



from common.models import OperationalUser
class Resource(models.Model):
    region = models.CharField(max_length=100,choices=REGION_CHOICES,null=True,blank=True)
    zone = models.CharField(max_length=100,choices=ZONE_CHOICES,null=True,blank=True)
    mp = models.CharField(max_length=100,choices=MP_CHOICES,null=True,blank=True)
    total_site = models.IntegerField(null=True, blank=True)
    no_of_KPI_site = models.IntegerField(null=True, blank=True)

    num_of_PGTL = models.IntegerField(null=True, blank=True)
    num_of_PGR = models.IntegerField(null=True, blank=True)
    num_of_adhoc_PGR = models.IntegerField(null=True, blank=True)

    num_of_vehicle = models.IntegerField(null=True, blank=True)
    num_of_good_PG = models.IntegerField(null=True, blank=True)
    num_of_faulty_PG = models.IntegerField(null=True, blank=True)
    num_of_adhoc_vehicle = models.IntegerField(null=True, blank=True)

    num_of_PG_repair_technician = models.IntegerField(null=True, blank=True)
    num_of_DG_repair_technician = models.IntegerField(null=True, blank=True)   
    num_of_admin_executive = models.IntegerField(null=True, blank=True)
    num_of_account_executive = models.IntegerField(null=True, blank=True)
  

    num_of_RM = models.IntegerField(null=True, blank=True)
    num_of_ZM = models.IntegerField(null=True, blank=True)
    num_of_AZM = models.IntegerField(null=True, blank=True)

    num_of_ebill = models.IntegerField(null=True, blank=True)
    num_of_reporter = models.IntegerField(null=True, blank=True)
    num_of_PM_engineer = models.IntegerField(null=True, blank=True)

    num_of_riger = models.IntegerField(null=True, blank=True)
    num_of_RMS_technician = models.IntegerField(null=True, blank=True)
    num_of_solar_expert = models.IntegerField(null=True, blank=True)

    num_of_rectifier_expert = models.IntegerField(null=True, blank=True)
    num_of_DGOW_runner = models.IntegerField(null=True, blank=True)
    num_of_petroller = models.IntegerField(null=True, blank=True)

    num_of_AC_IBS = models.IntegerField(null=True, blank=True)
   
    total_human_resource = models.IntegerField(null=True, blank=True)
    faulty_PG_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):     

        self.num_of_vehicle = AddVehicleInfo.objects.filter(
            region=self.region,
            zone=self.zone,
            mp=self.mp
        ).count()  
       
        self.num_of_adhoc_vehicle = AddVehicleInfo.objects.filter(
            region=self.region,
            zone=self.zone,
            mp=self.mp,
            vehicle_rental_type ='adhoc'

        ).count()

        self.num_of_good_PG = AddPGInfo.objects.filter(
            region=self.region,
            zone=self.zone,
            mp=self.mp,
            PG_status='good'
        ).count()

        self.num_of_faulty_PG = AddPGInfo.objects.filter(
            region=self.region,
            zone=self.zone,
            mp=self.mp,
            PG_status='faulty'
        ).count()
       
       ####################################################       
        self.num_of_RM = OperationalUser.objects.filter(
                    region=self.region,
                    zone=self.zone,
                    mp=self.mp,
                    user_designation='RM'
                ).count()

        self.num_of_ZM = OperationalUser.objects.filter(
                    region=self.region,
                    zone=self.zone,
                    mp=self.mp,
                    user_designation='ZM'
                ).count()
        self.num_of_AZM = OperationalUser.objects.filter(
                    region=self.region,
                    zone=self.zone,
                    mp=self.mp,
                    user_designation='AZM'
                ).count()
        
        self.num_of_PGR = PGRdatabase.objects.filter(
            region=self.region,
            zone=self.zone,
            mp=self.mp,    
            PGR_category ='permanent'     
        ).count()

        
        self.num_of_adhoc_PGR = PGRdatabase.objects.filter(
            region=self.region,
            zone=self.zone,
            mp=self.mp,    
            PGR_category ='adhoc'     
        ).count()

        self.num_of_PGTL = PGTLdatabase.objects.filter(
            region=self.region,
            zone=self.zone,
            mp=self.mp,          
        ).count()
     

        self.num_of_ebill = OperationalUser.objects.filter(
                    region=self.region,
                    zone=self.zone,
                    mp=self.mp,
                    user_designation='ebill'
                ).count()
        self.num_of_reporter = OperationalUser.objects.filter(
                    region=self.region,
                    zone=self.zone,
                    mp=self.mp,
                    user_designation='reporter'
                ).count()
        self.num_of_PM_engineer = OperationalUser.objects.filter(
                    region=self.region,
                    zone=self.zone,
                    mp=self.mp,
                    user_designation='PM_engineer'
                ).count()
        self.num_of_riger = OperationalUser.objects.filter(
                    region=self.region,
                    zone=self.zone,
                    mp=self.mp,
                    user_designation='riger'
                ).count()
        self.num_of_RMS_technician = OperationalUser.objects.filter(
                    region=self.region,
                    zone=self.zone,
                    mp=self.mp,
                    user_designation='RMS_expert'
                ).count()
        self.num_of_solar_expert = OperationalUser.objects.filter(
                    region=self.region,
                    zone=self.zone,
                    mp=self.mp,
                    user_designation='solar_expert'
                ).count()
        self.num_of_rectifier_expert = OperationalUser.objects.filter(
                    region=self.region,
                    zone=self.zone,
                    mp=self.mp,
                    user_designation='rectifier_expert'
                ).count()
        self.num_of_DGOW_runner = OperationalUser.objects.filter(
                    region=self.region,
                    zone=self.zone,
                    mp=self.mp,
                    user_designation='DGOW_runner'
                ).count()
        self.num_of_petroller = OperationalUser.objects.filter(
                    region=self.region,
                    zone=self.zone,
                    mp=self.mp,
                    user_designation='patroller'
                ).count()
        self.num_of_AC_IBS = OperationalUser.objects.filter(
                    region=self.region,
                    zone=self.zone,
                    mp=self.mp,
                    user_designation='AC_IBS'
                ).count()
        self.num_of_PG_repair_technician = OperationalUser.objects.filter(
                    region=self.region,
                    zone=self.zone,
                    mp=self.mp,
                    user_designation='PG_technician'
                ).count()
        self.num_of_DG_repair_technician = OperationalUser.objects.filter(
                    region=self.region,
                    zone=self.zone,
                    mp=self.mp,
                    user_designation='DG_technician'
                ).count()
        self.num_of_account_executive = OperationalUser.objects.filter(
                    region=self.region,
                    zone=self.zone,
                    mp=self.mp,
                    user_designation='Account_executive'
                ).count()
        self.num_of_admin_executive= OperationalUser.objects.filter(
                    region=self.region,
                    zone=self.zone,
                    mp=self.mp,
                    user_designation='Admin_executive'
                ).count()    

        self.total_human_resource = sum(filter(None, [
            self.num_of_PGTL,self.num_of_PGR,self.num_of_PG_repair_technician,
            self.num_of_DG_repair_technician,self.num_of_admin_executive,self.num_of_account_executive,
            self.num_of_ebill,self.num_of_reporter,self.num_of_PM_engineer,
            self.num_of_riger,self.num_of_RMS_technician,self.num_of_solar_expert,
            self.num_of_rectifier_expert,self.num_of_DGOW_runner,self.num_of_petroller,
            self.num_of_AC_IBS,self.num_of_RM,self.num_of_ZM,self.num_of_AZM
        ]))

        total_PG = self.num_of_good_PG + self.num_of_faulty_PG
        if total_PG:
            self.faulty_PG_percentage = self.num_of_faulty_PG / total_PG * 100
        else:
            self.faulty_PG_percentage = 0  

        super().save(*args, **kwargs)




