
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator

from account.models import Customer
from decimal import Decimal
from django.db import IntegrityError
from django.apps import apps

from common.models import Region,Zone,MP,FuelPumpDatabase



class AddVehicleInfo(models.Model):
    region = models.ForeignKey(Region,related_name='vehicle_region',on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone,related_name='vehicle_zone',on_delete=models.CASCADE)
    mp = models.ForeignKey(MP,related_name='vehicle_mp',on_delete=models.CASCADE)
    vehicle_id = models.CharField(max_length=50, default='None')
    vehicle_add_requester = models.ForeignKey(Customer, related_name='vehicle_add_user', on_delete=models.CASCADE)

    vehicle_owner_name= models.CharField(max_length=50, default='None')
    vehilce_owner_mobile_number = models.CharField(max_length=50, default='None')
    vehicle_owner_address = models.TextField(default='None')
    vehicle_owner_company_name = models.CharField(max_length=50, default='None')
    vehicle_reg_number = models.CharField(max_length=50, default='None')

    vehicle_kilometer_commit_per_liter = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True) 
    vehicle_money_commit_per_kilometer = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    
    vehicle_body_overtime_rate = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    vehicle_driver_overtime_rate = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    
    vehicle_joining_date = models.DateField(default=timezone.now)
    vehicle_cancel_date = models.DateField(null=True, blank=True, default=None)
   
    vehicle_supporting_documents = models.FileField(upload_to='vehicle_supporting_documents/', null=True, blank=True)
    
    vehicle_fuel_type_choices=[
        ('diesel','diesel'),
        ('octane', 'octane'),
        ('cng','cng'),
        ('taka','taka'),
    ]
    vehicle_fuel_type = models.CharField(max_length=50, choices=vehicle_fuel_type_choices, default='None')

    vehicle_fuel_unit_price = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
       
    vehicle_brand_choices=[
        ('toyota_pickup_single','toyota_pickup_single'),
        ('nissan_pickup_single', 'nissan_pickup_single'),
        ('tata_pickup_single','tata_pickup_single'),
        ('toyota_pickup_double','toyota_pickup_double'),
        ('nissan_pickup_double', 'nissan_pickup_double'),
        ('tata_pickup_double','tata_pickup_double'),
        ('toyota_private_car','toyota_private_car'),
        ('toyota_microbus','toyota_microbus'),
        ('others','others')
    ]
    vehicle_brand_name = models.CharField(max_length=50, choices= vehicle_brand_choices,default='None')

    rental_category_choices =[
        ('monthly','monthly'),
        ('daily','daily')
    ]
    vehicle_rental_category = models.CharField(max_length=50, choices=rental_category_choices, default='None')
    vehicle_rent = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)

    vehicle_operational_mode_choices =[
        ('corrective_maintenance','corrective_maintenance'),
        ('preventive_maintenance','preventive_maintenance'),
        ('others','others')
        ]
    vehicle_operational_mode = models.CharField(max_length=50,choices=vehicle_operational_mode_choices, default='None')
   
    
    vehicle_status_choice =[
       ('active','active'),
       ('cancel','cancel')
    ]
    vehicle_status = models.CharField(max_length=50, choices=vehicle_status_choice,default='None')
    
   
    created_at = models.DateField(default=timezone.now)

    def __str__(self):
            return self.vehicle_reg_number
    


class FuelRefill(models.Model):
    region = models.ForeignKey(Region,related_name='vehicle_refill_region',on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone,related_name='vehicle_refill_zone',on_delete=models.CASCADE)
    mp = models.ForeignKey(MP,related_name='vehicle_refill_mp',on_delete=models.CASCADE) 
    vehicle = models.ForeignKey(AddVehicleInfo, related_name='refills_info', on_delete=models.CASCADE)

    REFILL_CHOICES = [
        ('pump', 'pump'),
        ('local_purchase', 'Local Purchase')
    ]
    
    refill_type = models.CharField(max_length=20, choices=REFILL_CHOICES, default='pump')
   
    pump = models.ForeignKey(FuelPumpDatabase,related_name='vehicle_fuel_pump',on_delete=models.CASCADE,default=None,null=True,blank=True)
    refill_requester = models.ForeignKey(Customer, related_name='refill_requester_name', on_delete=models.CASCADE, null=True, blank=True)
    fuel_refill_code = models.CharField(max_length=50, default='None')
    refill_date = models.DateField(default=timezone.now)

    fuel_type_choices=[
        ('diesel','diesel'),
        ('octane','octane'),
        ('petrol','petrol'),
    ]         
    fuel_type =models.CharField(max_length=100, choices=fuel_type_choices,null=True, blank=True, default='None')        
   
    refill_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)   
    vehicle_kilometer_reading = models.DecimalField(max_digits=50, decimal_places=2, default=0.0)
    vehicle_kilometer_run = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    vehicle_fuel_consumed = models.DecimalField(max_digits=30, decimal_places=2, default=0.0)
    vehicle_fuel_balance = models.DecimalField(max_digits=30, decimal_places=2, default=0.0)
    vehicle_total_fuel_reserve = models.DecimalField(max_digits=30, decimal_places=2, default=0.0)
    refill_supporting_documents = models.FileField(upload_to='refill_supporting_documents/', null=True, blank=True)
    
    fuel_supplier_name = models.CharField(max_length=150,null=True,blank=True)                  
    fuel_supplier_phone = models.CharField(max_length=50, default='None')   
    fuel_supplier_address = models.TextField(default='None',null=True, blank=True)      
   
    created_at = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
            last_refill = FuelRefill.objects.filter(vehicle=self.vehicle).order_by('-refill_date').first()

            if last_refill:
                self.vehicle_kilometer_run = max(Decimal('0.0'), self.vehicle_kilometer_reading - last_refill.vehicle_kilometer_reading)
            else:
                self.vehicle_kilometer_run = Decimal('0.0') 

            self.running_hours = self.vehicle_kilometer_run / Decimal('10.0')

            if self.vehicle.vehicle_kilometer_commit_per_liter:
                self.vehicle_fuel_consumed = self.vehicle_kilometer_run / self.vehicle.vehicle_kilometer_commit_per_liter
                
            else:
                self.vehicle_fuel_consumed = Decimal('0.0')
               

            if last_refill:
                self.vehicle_fuel_balance = last_refill.refill_amount - self.vehicle_fuel_consumed
            else:
                 self.vehicle_fuel_balance = Decimal('0.0') 
            
            self.vehicle_total_fuel_reserve = self.refill_amount + self.vehicle_fuel_balance

            super().save(*args, **kwargs)

    def __str__(self):
            return self.fuel_supplier_phone



class VehicleRuniningData(models.Model):
    region = models.ForeignKey(Region,related_name='vehicle_run_region',on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone,related_name='vehicle_run_zone',on_delete=models.CASCADE)
    mp = models.ForeignKey(MP,related_name='vehicle_run_mp',on_delete=models.CASCADE)
    vehicle_expense_id = models.CharField(max_length=50, default='None')     
    vehicle = models.ForeignKey(AddVehicleInfo, related_name='vehicle_expense', on_delete=models.CASCADE) 
    fuel_refill = models.ForeignKey(FuelRefill, related_name='fuelexpenses', on_delete=models.CASCADE, null=True, blank=True)
    vehicle_expense_add_requester = models.ForeignKey(Customer, related_name='vehicle_expense_user', on_delete=models.CASCADE,null=True, blank=True)
   
    vehicle_start_reading = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    vehicle_stop_reading = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    vehicle_start_location = models.CharField(max_length=255, default='None')
    vehicle_end_location = models.CharField(max_length=255, default='None')
    travel_date = models.DateField(default=timezone.now)
    start_time= models.DateTimeField(default=timezone.now)    
    stop_time= models.DateTimeField(default=timezone.now)  
    travel_purpose = models.TextField(null=True,blank=True)    
    running_hours = models.FloatField(default=None, null=True, blank=True)
    overtime_hours = models.FloatField(default=None, null=True, blank=True)
    overtime_cost = models.FloatField(default=None, null=True, blank=True)
    
    total_kilometer_run = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_fuel_consumed = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    fuel_balance = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_fuel_cost = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
       
    comments = models.TextField(max_length=50,null=True,blank=True)   
    created_at = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):      
        if self.vehicle_stop_reading is not None and self.vehicle_start_reading is not None:
            try:   
                self.total_kilometer_run = Decimal(self.vehicle_stop_reading) - self.vehicle_start_reading
             
                if self.vehicle.vehicle_kilometer_commit_per_liter:          
                    self.total_fuel_consumed = self.total_kilometer_run / self.vehicle.vehicle_kilometer_commit_per_liter
                    
                if self.vehicle.vehicle_fuel_unit_price is not None:
                    self.total_fuel_cost = self.total_fuel_consumed * self.vehicle.vehicle_fuel_unit_price
                else:
                    self.total_fuel_cost = None
                             
            except IntegrityError:
                pass
        
        if self.start_time and self.stop_time:
            if self.start_time.date() != self.stop_time.date():
                raise ValueError("Start time and stop time must be on the same day.")            
            running_hours_timedelta = self.stop_time - self.start_time
            self.running_hours = running_hours_timedelta.total_seconds() / 3600
           
        super(VehicleRuniningData, self).save(*args, **kwargs)




class Vehiclefault(models.Model):
    region = models.ForeignKey(Region,related_name='vehicle_fault_region',on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone,related_name='vehicle_fault_zone',on_delete=models.CASCADE)
    mp = models.ForeignKey(MP,related_name='vehicle_fault_mp',on_delete=models.CASCADE)
    vehicle_fault_id = models.CharField(max_length=50, default='None')    
    vehicle = models.ForeignKey(AddVehicleInfo, related_name='vehiclefault_info', on_delete=models.CASCADE,null=True, blank=True)
    vehicle_runnin_data = models.ForeignKey(VehicleRuniningData, related_name='VehicleRuniningDataInfo', on_delete=models.CASCADE ,null=True, blank=True) 
    vehicle_user = models.ForeignKey(Customer, related_name='vehicle_fault_user', on_delete=models.CASCADE, null=True, blank=True)
    fault_start_time = models.DateTimeField(default=timezone.now)    
    fault_stop_time = models.DateTimeField(default=timezone.now)  
    fault_duration_hours = models.FloatField(default=None, null=True, blank=True)
    fault_location = models.CharField(max_length=255, default='None',null=True, blank=True)
    fault_type_choices=[
        ('accident','accident'),
        ('engine_stop','engine_stop'),
        ('tyre_punchure','tyre_punchure'),
        ('others','others')
    ]
    fault_type = models.CharField(max_length=255,choices=fault_type_choices,default='None',null=True, blank=True)
    created_at = models.DateField(default=timezone.now)


    def save(self, *args, **kwargs):       
        try:   
           fault_hours = self.fault_stop_time - self.fault_start_time
           self.fault_duration_hours = fault_hours.total_seconds() / 3600
        except IntegrityError:
            pass

        super(Vehiclefault, self).save(*args, **kwargs)




class VehicleRentalCost(models.Model):
    region = models.ForeignKey(Region,related_name='vehicle_pay_region',on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone,related_name='vehicle_pay_zone',on_delete=models.CASCADE)
    mp = models.ForeignKey(MP,related_name='vehicle_pay_mp',on_delete=models.CASCADE)
    vehicle_rent_paid_id = models.CharField(max_length=50, default='None')     

    vehicle_rent_paid = models.CharField(max_length=50, default='None') 
    vehicle_body_overtime_paid = models.CharField(max_length=50, default='None') 
    vehicle_driver_overtime_paid = models.CharField(max_length=50, default='None')         
      
    vehicle = models.ForeignKey(AddVehicleInfo, related_name='vehiclerent_info', on_delete=models.CASCADE) 
   
    
    comments = models.TextField(max_length=50, default='None')   
    created_at = models.DateField(default=timezone.now)


