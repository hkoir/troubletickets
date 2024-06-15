from django.db import models
from django.utils import timezone
from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES
from account.models import Customer




class Region(models.Model):
    name = models.CharField(max_length=100,)
    def __str__(self):
        return self.name

class Zone(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='zones')

    def __str__(self):
        return self.name

class MP(models.Model):
    name = models.CharField(max_length=100)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='mps')
    def __str__(self):
        return self.name





class AddPGInfo(models.Model):
    region = models.ForeignKey(Region,related_name='pg_region',on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone,related_name='pg_zone',on_delete=models.CASCADE)
    mp = models.ForeignKey(MP,related_name='pg_mp',on_delete=models.CASCADE)
    PG_code = models.CharField(max_length=50, default='None')
    PG_add_requester = models.ForeignKey(Customer, related_name='PGad_admin_user', on_delete=models.CASCADE)
    PGNumber = models.CharField(max_length=50,default='None')
    PG_brand_choices=[
        ('Honda','Honda'),
        ('Mistsubishi', 'Mistsubishi'),
        ('wilson','wilson'),
        ('chinese','chinese'),       
    ]
    PG_brand = models.CharField(max_length=50, choices= PG_brand_choices,default='None')
    PG_serial_number = models.CharField(max_length=50,default='None')

    PG_capacity_choices=[
        ('5kva','5kva'),
        ('6kva','6kva'),
        ('8kva','8kva')
        ]
    PG_capacity = models.CharField(max_length=50,choices=PG_capacity_choices,default='None')

    PG_supplier_choices=[
        ('vendor1','vendor1'),
        ('vendor2','vendor2'),
        ('vendor3','vendor3'),
        ('own','own'),
    ]

    PG_supplier=models.CharField(max_length=50,choices=PG_supplier_choices,default='None')
    
    PG_status_choices =[
        ('good','good'),
        ('faulty','faulty')
    ]
    PG_status = models.CharField(max_length=100, choices=PG_status_choices,null=True,blank=True)
    PG_purchase_date = models.DateField(default=timezone.now)
    PG_hire_date = models.DateField(default=timezone.now)
    PG_supporting_documents = models.FileField(upload_to='PG_documents/', null=True, blank=True)
    
    
    created_at = models.DateField(default=timezone.now)
    updated_at = models.DateField(default=timezone.now)

    # def __str__(self):
    #         return self.PGNumber
    def __str__(self):
        return f"{self.region.name} - {self.zone.name} - {self.mp.name} - {self.PG_status} - {self.PGNumber}"




class FuelPumpDatabase(models.Model):
    region = models.ForeignKey(Region,related_name='fuel_pump_region',on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone,related_name='fuel_pump_zone',on_delete=models.CASCADE)
    mp = models.ForeignKey(MP,related_name='fuel_pump_mp',on_delete=models.CASCADE)
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
    contact_period = models.DurationField(null=True,blank=True)
    created_at = models.DateField(default=timezone.now)

class fuelPumpPayment(models.Model):
    pump = models.ForeignKey(FuelPumpDatabase,related_name='fuel_pump_pay_data',on_delete=models.CASCADE)
    payment_amount =models.DecimalField(max_digits=15,decimal_places=2,null=True,blank=True)
    payment_date = models.DateField(null=True,blank=True,default=None)
    payment_id = models.CharField(max_length=100, default='None',null=True,blank=True)
    created_at =models.DateField(default=timezone.now)
 

class PGFuelRefill(models.Model):
    region = models.ForeignKey(Region,related_name='pg_refill_region',on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone,related_name='pg_refill_zone',on_delete=models.CASCADE)
    mp = models.ForeignKey(MP,related_name='pg_refill_mp',on_delete=models.CASCADE)   
    refill_requester = models.ForeignKey(Customer, related_name='pg_refill_requester_name', on_delete=models.CASCADE, null=True, blank=True)
    fuel_refill_code = models.CharField(max_length=50, default='None')
    refill_date = models.DateField(default=timezone.now)
  
    pgnumber =models.ForeignKey(AddPGInfo, related_name='pginfo', on_delete=models.CASCADE, null=True, blank=True)      
    fuel_type_choices=[
        ('diesel','diesel'),
        ('octane','octane'),
        ('petrol','petrol'),
    ]         
    fuel_type =models.CharField(max_length=100, choices=fuel_type_choices,null=True, blank=True, default='None')

    refill_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)   
    fuel_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)    
    fuel_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0,null=True, blank=True)  
    refill_supporting_documents = models.FileField(upload_to='PG_refill_slips/', null=True, blank=True)

    fuel_pump = models.ForeignKey(FuelPumpDatabase,related_name='pump_data_info',on_delete=models.CASCADE,default=None)
    fuel_supplier_phone = models.CharField(max_length=50, default='None')   
    fuel_supplier_address = models.TextField(default='None',null=True, blank=True)   
       
    created_at = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):      
      if self. refill_amount is not None:
        self.fuel_cost = self.refill_amount * self.fuel_rate
           
        super(PGFuelRefill, self).save(*args, **kwargs)


   
    def __str__(self):
            return self.fuel_pump_supplier_name


class PGFaultRecord(models.Model):
     region = models.ForeignKey(Region,related_name='pg_fault_region',on_delete=models.CASCADE)
     zone = models.ForeignKey(Zone,related_name='pg_fault_zone',on_delete=models.CASCADE)
     mp = models.ForeignKey(MP,related_name='pg_fault_mp',on_delete=models.CASCADE)
     pgnumber =models.ForeignKey(AddPGInfo, related_name='pgfaultinfo', on_delete=models.CASCADE, null=True, blank=True)  
     fault_date = models.DateField(null=True, blank=True)
     repair_date = models.DateField(null=True, blank=True)
     fault_duration = models.DurationField(null=True, blank=True)
     fault_description = models.TextField(max_length=200,null=True, blank=True,)

     fault_type_choices=[
         ('air_filter_problem','air_filter_problem'),
         ('oil_filter_problem','oil_filter_problem'),
         ('engine_problem','engine_problem'),
         ('others','others')
     ]
     fault_type = models.CharField(max_length=200,choices=fault_type_choices,null=True, blank=True,)
     action_taken = models.CharField(max_length=200,null=True, blank=True,)
     repair_by = models.CharField(max_length=100, null=True,blank=True)
     repair_cost = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)  
     created_at = models.DateField(default=timezone.now)
     updated_at = models.DateField(default=timezone.now)
    
     def save(self, *args, **kwargs):
        if self.fault_date and self.repair_date:
            self.fault_duration = self.repair_date - self.fault_date
        else:
            self.fault_duration = None
        super().save(*args, **kwargs)


