from django.db import models
from django.utils import timezone
from datetime import datetime
from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES





class Notice(models.Model):
    title = models.CharField(max_length=255,null=True,blank=True)
    content = models.TextField(null=True,blank=True)
    notice_image = models.ImageField(upload_to='notices',null=True,blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title




class FuelPumpDatabase(models.Model):
    region = models.CharField(max_length=100,choices=REGION_CHOICES,null=True,blank=True)
    zone = models.CharField(max_length=100,choices=ZONE_CHOICES,null=True,blank=True)
    mp = models.CharField(max_length=100,choices= MP_CHOICES,null=True,blank=True)
    fuel_pump_name = models.CharField(max_length=100,null=True,blank=True)
    fuel_pump_id = models.CharField(max_length=50, default='None',null=True,blank=True)  
    fuel_pump_company_name = models.CharField(max_length=100,null=True,blank=True)
    fuel_pump_phone = models.CharField(max_length=100,null=True,blank=True)
    fuel_pump_email = models.EmailField(null=True,blank=True)
    fuel_pump_address = models.TextField(null=True,blank=True)     
    pump_type_choices=[
        ('prepaid','prepaid'),
        ('postpaid','postpaid')
    ]
    fuel_pump_type = models.CharField(max_length=100,choices=pump_type_choices,null=True,blank=True)
    fuel_pump_supporting_documents = models.FileField(upload_to='fuel_pump_supporting_documents/', null=True, blank=True)
    advance_amount_given = models.DecimalField(max_digits=20,decimal_places=2,null=True,blank=True)
    contact_date = models.DateField(null=True,blank=True)    
    contact_period = models.DecimalField(max_digits=10, decimal_places=1,null=True,blank=True)
    created_at = models.DateField(default=timezone.now)

    def __str__(self):
        return self.fuel_pump_name
    


class fuelPumpPayment(models.Model):
    pump = models.ForeignKey(FuelPumpDatabase,related_name='fuel_pump_pay_data',on_delete=models.CASCADE)
    payment_amount =models.DecimalField(max_digits=15,decimal_places=2,null=True,blank=True)
    payment_date = models.DateField(null=True,blank=True,default=None)
    payment_id = models.CharField(max_length=100, default='None',null=True,blank=True)
    payment_document = models.ImageField(upload_to="fuel_pump_payment", null=True,blank=True)
    created_at =models.DateField(default=timezone.now)
 



class PGTLdatabase(models.Model):  
    region = models.CharField(max_length=100,choices=REGION_CHOICES,null=True,blank=True)
    zone = models.CharField(max_length=100,choices=ZONE_CHOICES,null=True,blank=True)
    mp = models.CharField(max_length=100,choices= MP_CHOICES,null=True,blank=True)
    name = models.CharField(max_length=100)    
    pgtl_id = models.CharField(max_length=150,null=True, blank=True)
    phone = models.CharField(max_length=100)
    payment_number= models.CharField(max_length=100,null=True,blank=True)
    payment_option=[
        ('bikash','biksah'),
        ('nagad','nagad'),
        ('rocket','rocket'),
    ]
    payment_number_choice = models.CharField(max_length=100,choices=payment_option,null=True,blank=True, default='bikash')
 
    email = models.EmailField()
    address = models.TextField()
    PGTL_photo = models.ImageField(upload_to='PGTL_photo', blank=True, null=True) 
    PGTL_birth_certificate = models.FileField(upload_to='PGTL_birth_certificate',blank=True, null=True)
    joining_date=models.DateField(null=True,blank=True)
    PGTL_salary = models.DecimalField(max_digits=15,decimal_places=2,null=True,blank=True)
    reference_person_name = models.CharField(max_length=100,null=True,blank=True)
    reference_person_phone = models.CharField(max_length=100,null=True,blank=True)
    created_at = models.DateField(default=timezone.now)

    def __str__(self):
        return self.name


class PGRdatabase(models.Model):
    region = models.CharField(max_length=100, choices=REGION_CHOICES, null=True, blank=True)
    zone = models.CharField(max_length=100, choices=ZONE_CHOICES, null=True, blank=True)
    mp = models.CharField(max_length=100, choices=MP_CHOICES, null=True, blank=True)
    name = models.CharField(max_length=100)
    pgr_id = models.CharField(max_length=150, null=True, blank=True)
    pgtl = models.ForeignKey(PGTLdatabase, on_delete=models.CASCADE, null=True, blank=True)
    PGR_category_choices = [
        ('adhoc', 'adhoc'),
        ('permanent', 'permanent')]
    PGR_category = models.CharField(max_length=100, choices=PGR_category_choices, default='adhoc', null=True, blank=True)
    
    pgr_payment_type_choices=[
        ('monthly','monthly'),
        ('hourly','hourly'),
        ('12hours','12hours'),
        ('24hours','24hours')
    ]
    PGR_payment_type = models.CharField(max_length=100,choices=pgr_payment_type_choices, null=True,blank=True)
   
    PGR_pay_rate = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    phone = models.CharField(max_length=100)
    payment_number= models.CharField(max_length=100,null=True,blank=True)
    payment_option=[
        ('bikash','biksah'),
        ('nagad','nagad'),
        ('rocket','rocket'),
    ]
    payment_number_choice = models.CharField(max_length=100,choices=payment_option,null=True,blank=True,default='bikash')
    email = models.EmailField()
    address = models.TextField()
    PGR_photo = models.ImageField(upload_to='PGR_photo', blank=True, null=True)
    PGR_birth_certificate = models.FileField(upload_to='PGR_birth_certificate', blank=True, null=True)
    joining_date = models.DateField(null=True, blank=True)
    reference_person_name = models.CharField(max_length=100, null=True, blank=True)
    reference_person_phone = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateField(default=timezone.now)

    def __str__(self):
        return self.name
    



class OperationalUser(models.Model):
    region = models.CharField(max_length=100, choices=REGION_CHOICES, null=True, blank=True)
    zone = models.CharField(max_length=100, choices=ZONE_CHOICES, null=True, blank=True)
    mp = models.CharField(max_length=100, choices=MP_CHOICES, null=True, blank=True)
    user_name = models.CharField(max_length=100,null=True)
    user_type_choices=[
        ('CM_user','CM_user'),
        ('PM_user','PM_user'),
        ('others','others'),
    ]
    user_type = models.CharField(max_length=50,choices= user_type_choices,null=True)
    designation_choices=[
        ('RM','RM'),
        ('ZM','ZM'),
        ('AZM','AZM'),
        ('rectifer_expert','rectifier_expert'),
        ('DGOW_runner','DGOW_runner'),
        ('patroller','patroller'),
        ('AC_IBS','AC_IBS'),
        ('riger','riger'),
        ('RMS_expert','RMS_expert'),
        ('solar_expert','solar_expert'),
        ('ebill','ebill'),
        ('reporter','reporter'),
        ('PM_engineer','PM_engineer'),
        ('PG_technician','PG_technician'),
        ('DG_technician','DG_technician'),
        ('Admin_executive','Admin_executive'),
        ('Account_executive','Account_executive'),
        ('General_staff','General_staff')

    ]
    user_designation =models.CharField(max_length=50,choices=designation_choices,null=True)
    phone = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    user_photo = models.ImageField(upload_to='user_photo', blank=True, null=True)
    user_birth_certificate = models.FileField(upload_to='user_birth_certificate', blank=True, null=True)
    joining_date = models.DateField(null=True, blank=True)
    reference_person_name = models.CharField(max_length=100, null=True, blank=True)
    reference_person_phone = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateField(default=timezone.now)

    def __str__(self):
        return self.user_name

