
from django.db import models
from django.utils import timezone
from datetime import datetime,timedelta
from django.core.validators import FileExtensionValidator
from account.models import Customer
from decimal import Decimal
from django.db import IntegrityError,models
from django.apps import apps
from common.models import FuelPumpDatabase
from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES
from decimal import Decimal




class AddVehicleInfo(models.Model):
    region = models.CharField(max_length=100,choices=REGION_CHOICES,null=True,blank=True)
    zone = models.CharField(max_length=100,choices=ZONE_CHOICES,null=True,blank=True)
    mp = models.CharField(max_length=100,choices=MP_CHOICES,null=True,blank=True)
    vehicle_id = models.CharField(max_length=50, default='None')
    vehicle_add_requester = models.ForeignKey(Customer, related_name='vehicle_add_user', on_delete=models.CASCADE)

    vehicle_owner_name= models.CharField(max_length=50, default='None')
    vehilce_owner_mobile_number = models.CharField(max_length=50, default='None')
    vehicle_owner_address = models.TextField(default='None')
    vehicle_owner_company_name = models.CharField(max_length=50, default='None')
    vehicle_reg_number = models.CharField(max_length=50, default='None')

    vehicle_kilometer_commit_per_liter = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True) 
    vehicle_money_commit_per_kilometer_gasoline = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    vehicle_money_commit_per_kilometer_CNG = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    vehicle_max_kilometer_CNG = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)

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
    vehicle_hour_contact_choices=[
        ('12 hours','12 hour'),
        ('24 hours','24 hours')
    ]
    vehicle_hour_contact = models.CharField(max_length=100,choices=vehicle_hour_contact_choices,null=True,blank=True)
   
    vehicle_rental_type_choices=[
        ('permanent','permanent'),
        ('adhoc','adhoc')
    ]
    vehicle_rental_type = models.CharField(max_length=50, choices=vehicle_rental_type_choices,null=True,blank=True, default='None')
    vehicle_rent = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    vehicle_rent_per_day = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)

    vehicle_operational_mode_choices =[
        ('CM_vehicle','CM_vehicle'),
        ('PM_vehicle','PM_vehicle'),
        ('others','others')
        ]
    vehicle_operational_mode = models.CharField(max_length=50,choices=vehicle_operational_mode_choices, default='None')
       
    vehicle_status_choice =[
       ('active','active'),
       ('cancel','cancel')
    ]
    vehicle_status = models.CharField(max_length=50, choices=vehicle_status_choice,default='None')
    created_at = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.vehicle_rental_category == 'daily':
            self.vehicle_rental_type ='adhoc'
        else:
            self.vehicle_rental_type ='permanent'

        if self.vehicle_rental_category == 'monthly':
            self.vehicle_rent_per_day =self.vehicle_rent / 30
        else:
            self.vehicle_rent_per_day = self.vehicle_rent
        
           
        super().save(*args, **kwargs)


    def __str__(self):
        return self.vehicle_reg_number
    


class FuelRefill(models.Model):
    region = models.CharField(max_length=100,choices=REGION_CHOICES,null=True,blank=True)
    zone = models.CharField(max_length=100,choices=ZONE_CHOICES,null=True,blank=True)
    mp = models.CharField(max_length=100,choices=MP_CHOICES,null=True,blank=True)
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
        ('CNG','CNG')
    ]         
    fuel_type =models.CharField(max_length=100, choices=fuel_type_choices,null=True, blank=True, default='None')        
    fuel_rate = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    refill_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    fuel_cost = models.DecimalField(max_digits=15,decimal_places=2,null=True,blank=True)
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
            if self.refill_amount is not None and self.pump is not None:
                self.fuel_cost = self.refill_amount * self.fuel_rate
            else:
                self.fuel_cost = self.refill_amount * self.fuel_rate        
            last_refill = FuelRefill.objects.filter(vehicle=self.vehicle).order_by('-refill_date').first()
            if last_refill:
                self.vehicle_kilometer_run = max(Decimal('0.0'), self.vehicle_kilometer_reading - last_refill.vehicle_kilometer_reading)               
            else:
                self.vehicle_kilometer_run = Decimal('0.0') 
            # self.running_hours = self.vehicle_kilometer_run / Decimal('10.0')
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
            return self.vehicle.vehicle_reg_number



class VehicleRuniningData(models.Model):
    region = models.CharField(max_length=100, choices=REGION_CHOICES, null=True, blank=True)
    zone = models.CharField(max_length=100, choices=ZONE_CHOICES, null=True, blank=True)
    mp = models.CharField(max_length=100, choices=MP_CHOICES, null=True, blank=True)
    vehicle_expense_id = models.CharField(max_length=50, default='None')
    vehicle = models.ForeignKey(AddVehicleInfo, related_name='vehicle_expense', on_delete=models.CASCADE)
    fuel_refill = models.ForeignKey(FuelRefill, related_name='fuelexpenses', on_delete=models.CASCADE, null=True, blank=True)
    vehicle_expense_add_requester = models.ForeignKey(Customer, related_name='vehicle_expense_user', on_delete=models.CASCADE, null=True, blank=True)
    vehicle_start_reading = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    vehicle_stop_reading = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    total_kilometer_run = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    vehicle_start_location = models.CharField(max_length=255, default='None')
    vehicle_end_location = models.CharField(max_length=255, default='None')
    start_time = models.DateTimeField(default=timezone.now)
    stop_time = models.DateTimeField(default=timezone.now)
    running_hours = models.FloatField(default=None, null=True, blank=True)
    overtime_hours = models.FloatField(default=None, null=True, blank=True)
    travel_date = models.DateField(default=timezone.now)
    travel_purpose = models.TextField(null=True, blank=True)   
    overtime_cost = models.FloatField(default=None, null=True, blank=True)
    day_end_kilometer_run = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)    
    day_end_kilometer_cost_CNG = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    day_end_kilometer_cost_gasoline = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_kilometer_cost = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_fuel_consumed = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    fuel_balance = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_fuel_cost = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    vehicle_rent_per_day = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    weekend_status = models.CharField(max_length=50,null=True,blank=True)  
    comments = models.TextField(max_length=50, null=True, blank=True)
    created_at = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.vehicle_stop_reading is not None and self.vehicle_start_reading is not None:
            try:
                self.total_kilometer_run = Decimal(self.vehicle_stop_reading) - Decimal(self.vehicle_start_reading)
                
                if self.vehicle.vehicle_kilometer_commit_per_liter:
                    self.total_fuel_consumed = self.total_kilometer_run / Decimal(self.vehicle.vehicle_kilometer_commit_per_liter)
                
                if self.vehicle.vehicle_fuel_unit_price is not None:
                    self.total_fuel_cost = self.total_fuel_consumed * Decimal(self.vehicle.vehicle_fuel_unit_price)
                else:
                    self.total_fuel_cost = None
                
                if self.total_kilometer_run is not None:
                    if self.total_kilometer_run <= Decimal(self.vehicle.vehicle_max_kilometer_CNG):
                        self.day_end_kilometer_cost_CNG = Decimal(self.total_kilometer_run) * Decimal(self.vehicle.vehicle_money_commit_per_kilometer_CNG)
                        self.day_end_kilometer_cost_gasoline = Decimal(0.0)
                        self.total_kilometer_cost= self.day_end_kilometer_cost_CNG + self.day_end_kilometer_cost_gasoline
                    else:
                        self.day_end_kilometer_cost_CNG = Decimal(self.vehicle.vehicle_max_kilometer_CNG) * Decimal(self.vehicle.vehicle_money_commit_per_kilometer_CNG)
                        self.day_end_kilometer_cost_gasoline = Decimal(self.total_kilometer_run - self.vehicle.vehicle_max_kilometer_CNG) * Decimal(self.vehicle.vehicle_money_commit_per_kilometer_gasoline)
                        self.total_kilometer_cost = self.day_end_kilometer_cost_CNG + self.day_end_kilometer_cost_gasoline
                self.total_kilometer_cost= self.day_end_kilometer_cost_CNG + self.day_end_kilometer_cost_gasoline
            except IntegrityError:
                pass
        
        if self.start_time and self.stop_time:
            if self.start_time.date() != self.stop_time.date():
                raise ValueError("Start time and stop time must be on the same day.")
            running_hours_timedelta = self.stop_time - self.start_time
            self.running_hours = running_hours_timedelta.total_seconds() / 3600
            
        if self.travel_date.weekday() in [4, 5]:
            self.weekend_status = 'weekend'
        else:
            self.weekend_status = 'weekday'
        
        if self.vehicle.vehicle_rental_category == 'monthly':                  
            self.vehicle_rent_per_day = self.vehicle.vehicle_rent / 30

        super(VehicleRuniningData, self).save(*args, **kwargs)

    def __str__(self):
        return self.vehicle.vehicle_reg_number


class Vehiclefault(models.Model):
    region = models.CharField(max_length=100,choices=REGION_CHOICES,null=True,blank=True)
    zone = models.CharField(max_length=100,choices=ZONE_CHOICES,null=True,blank=True)
    mp = models.CharField(max_length=100,choices=MP_CHOICES,null=True,blank=True)
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

    def __str__(self):
        return self.vehicle.vehicle_reg_number
  


class VehicleRentalCost(models.Model):
    region = models.CharField(max_length=100,choices=REGION_CHOICES,null=True,blank=True)
    zone = models.CharField(max_length=100,choices=ZONE_CHOICES,null=True,blank=True)
    mp = models.CharField(max_length=100,choices=MP_CHOICES,null=True,blank=True)
    vehicle_rent_paid_id = models.CharField(max_length=50, default='None')     

    vehicle_rent_paid = models.FloatField(default=0.0, null=True, blank=True)
    vehicle_body_overtime_paid = models.FloatField(default=0.0, null=True, blank=True)
    vehicle_driver_overtime_paid =models.FloatField(default=0.0, null=True, blank=True)
    
    vehicle_kilometer_paid =models.FloatField(default=0.0, null=True, blank=True)
    vehicle_total_paid = models.FloatField(default=0.0, null=True, blank=True)
   
    vehicle = models.ForeignKey(AddVehicleInfo, related_name='vehiclerent_info', on_delete=models.CASCADE) 
    comments = models.TextField(max_length=50, default='None',null=True,blank=True)   
    created_at = models.DateField(default=timezone.now)
   
    def save(self, *args, **kwargs):
        if self.vehicle_rent_paid is not None and self.vehicle_kilometer_paid is not None  and self.vehicle_body_overtime_paid is not None and self.vehicle_driver_overtime_paid is not None:
            self.vehicle_total_paid = self.vehicle_rent_paid + self.vehicle_body_overtime_paid + self.vehicle_driver_overtime_paid + self.vehicle_kilometer_paid
        
        
        super().save(*args, **kwargs)  # Ensure the changes are saved

    
    def __str__(self):
        return self.vehicle.vehicle_reg_number
  


############ adhoc vehicle requisition and payment control mechanism ##################

class AdhocVehicleRequisition(models.Model): 
    vehicle = models.ForeignKey(AddVehicleInfo, on_delete=models.CASCADE,blank=True,null=True)
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
    num_of_days_applied = models.IntegerField(null=True, blank=True)
    num_of_days_approved= models.IntegerField(null=True, blank=True) 
    requisition_id= models.CharField(max_length=50,null=True, blank=True, default='None')
    requester = models.ForeignKey(Customer,related_name='adhovehicle',on_delete=models.CASCADE,null=True,blank=True)   
    purpose = models.TextField(null=True,blank=True) 
    requisition_date = models.DateField(default=timezone.now)
    active_status = models.BooleanField(default=False)

    APPROVAL_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    approval_status = models.CharField(max_length=50, choices=APPROVAL_STATUS_CHOICES, default='PENDING')
           
    level1_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='level1_approval_adhocvehicle', null=True, blank=True)
    level2_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='level2_approval_adhocvehicle', null=True, blank=True)
    level3_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='level3_approval_adhocvehicle', null=True, blank=True)
    
    level1_approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='PENDING',null=True, blank=True)
    level2_approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='PENDING',null=True, blank=True)
    level3_approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='PENDING',null=True, blank=True)
    
    level1_comments = models.TextField(null=True, blank=True)
    level2_comments = models.TextField(null=True, blank=True)
    level3_comments = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now,null=True, blank=True)
    update_at = models.DateTimeField(auto_now=True)  # Changed to auto_now for automatic update timestamp

    level1_approval_date = models.DateTimeField(null=True, blank=True)
    level2_approval_date = models.DateTimeField(null=True, blank=True)
    level3_approval_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            if self.start_date == self.end_date:
                self.num_of_days_applied = 1
            else:
                self.num_of_days_applied = (self.end_date - self.start_date).days + 1

        level1_approved = self.level1_approval_status and self.level1_approval_status.lower() == 'approved'
        level2_approved = self.level2_approval_status and self.level2_approval_status.lower() == 'approved'
        level3_approved = self.level3_approval_status and self.level3_approval_status.lower() == 'approved'

        if level1_approved and level2_approved and level3_approved:
            self.approval_status = 'Approved'
        else:
             self.approval_status = 'Pending'        
        
        super().save(*args, **kwargs)  # Ensure the changes are saved

    def __str__(self):
        return f"Requisition for {self.vehicle.vehicle_reg_number} requisition_ID {self.requisition_id}"
  



class AdhocVehiclePayment(models.Model):   
    payment_id = models.CharField(max_length=150, null=True, blank=True)
    vehicle = models.ForeignKey(AddVehicleInfo, on_delete=models.CASCADE, null=True, blank=True)   
    adhoc_paid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_mode_choices = [
        ('bikash', 'bikash'),
        ('rocket', 'rocket'),
        ('nagad', 'nagad'),
        ('bank_transfer', 'bank_transfer'),
        ('others','others')
    ]
    payment_mode = models.CharField(max_length=100, choices=payment_mode_choices, null=True, blank=True)
    transaction_id = models.CharField(max_length=50, null=True, blank=True)
    payment_supporting_document = models.ImageField(upload_to='adhoc_vehicle_payment', null=True, blank=True)
    created_at = models.DateField(default=timezone.now)    

    def __str__(self):
        return self.vehicle.vehicle_reg_number



class AdhocVehicleAttendance(models.Model):
    vehicle = models.ForeignKey(AddVehicleInfo, related_name='vehicle_attendance', on_delete=models.CASCADE)
    vehicle_running_data = models.ForeignKey(VehicleRuniningData, related_name='vehicle_running_data', on_delete=models.CASCADE, null=True, blank=True)
    vehicle_fault = models.ForeignKey(Vehiclefault, related_name="vehicle_fault", on_delete=models.CASCADE, null=True, blank=True)
    adhoc_in_date = models.DateField(null=True, blank=True)
    adhoc_in_time = models.TimeField(null=True, blank=True)
    adhoc_out_date = models.DateField(null=True, blank=True)
    adhoc_out_time = models.TimeField(null=True, blank=True)
    adhoc_working_hours = models.FloatField(null=True, blank=True)
   
    adhoc_vehicle_base_bill_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    adhoc_vehicle_overtime_bill_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    adhoc_vehicle_total_bill_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    adhoc_payment = models.ForeignKey(AdhocVehiclePayment, related_name='adhoc_vehicle_payment_ref', on_delete=models.CASCADE, null=True, blank=True)
    adhoc_due_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    adhoc_requisition_vehicle = models.ForeignKey(AdhocVehicleRequisition, related_name='adhoc_vehicle_requisition_ref', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):      
        self.vehicle_running_data = VehicleRuniningData.objects.filter(
            vehicle=self.vehicle,         
            ).first()
            
        self.vehicle_fault = Vehiclefault.objects.filter(
                vehicle=self.vehicle,              
            ).first()
                

        if self.vehicle_running_data:
            self.adhoc_kilometer_run = self.vehicle_running_data.total_kilometer_run

        if self.adhoc_in_date and self.adhoc_in_time and self.adhoc_out_date and self.adhoc_out_time:
            in_datetime = datetime.combine(self.adhoc_in_date, self.adhoc_in_time)
            out_datetime = datetime.combine(self.adhoc_out_date, self.adhoc_out_time)
            total_seconds = (out_datetime - in_datetime).total_seconds()
            self.adhoc_working_hours = total_seconds / 3600

            if self.vehicle.vehicle_hour_contact =='12 hours':
                if self.adhoc_working_hours <= 12:
                    self.adhoc_vehicle_base_bill_amount = Decimal(self.vehicle.vehicle_rent)
                    self.adhoc_vehicle_overtime_bill_amount = Decimal(0)
                else:
                    division_result, division_remainder = divmod(self.adhoc_working_hours, 12)
                    self.adhoc_vehicle_base_bill_amount = Decimal(self.vehicle.vehicle_rent) * Decimal(division_result)
                    self.adhoc_vehicle_overtime_bill_amount = Decimal(division_remainder) * Decimal(self.vehicle.vehicle_body_overtime_rate)
           
            if self.vehicle.vehicle_hour_contact =='24 hours':
                if self.adhoc_working_hours <= 24:
                    self.adhoc_vehicle_base_bill_amount = Decimal(self.vehicle.vehicle_rent)
                    self.adhoc_vehicle_overtime_bill_amount = Decimal(0)
                else:
                    division_result, division_remainder = divmod(self.adhoc_working_hours, 24)
                    self.adhoc_vehicle_base_bill_amount = Decimal(self.vehicle.vehicle_rent) * Decimal(division_result)
                    self.adhoc_vehicle_overtime_bill_amount = Decimal(division_remainder) * Decimal(self.vehicle.vehicle_body_overtime_rate)


        if self.adhoc_vehicle_base_bill_amount is not None and self.adhoc_vehicle_overtime_bill_amount is not None:
            self.adhoc_vehicle_total_bill_amount = self.adhoc_vehicle_base_bill_amount + self.adhoc_vehicle_overtime_bill_amount

        # self.adhoc_due_amount = float(self.adhoc_vehicle_total_bill_amount) + float(self.vehicle_running_data.total_kilometer_cost) - float(self.adhoc_payment.adhoc_paid_amount)
       
        if self.adhoc_payment is not None and self.adhoc_payment.adhoc_paid_amount is not None and self.adhoc_vehicle_total_bill_amount is not None:
            self.adhoc_due_amount = float(self.adhoc_vehicle_total_bill_amount) - float(self.adhoc_payment.adhoc_paid_amount)
       
        super(AdhocVehicleAttendance, self).save(*args, **kwargs)

    def get_active_requisition(self):
        if not self.adhoc_in_date:
            return None
        try:
            requisition = AdhocVehicleRequisition.objects.get(
                vehicle=self.vehicle,
                active_status = True,              
                start_date__lte=self.adhoc_in_date,
                end_date__gte=self.adhoc_in_date,
                level1_approval_status='Approved'
            )
            return requisition
        except AdhocVehicleRequisition.DoesNotExist:
            return None
        
    
    def __str__(self):
        return self.vehicle.vehicle_reg_number