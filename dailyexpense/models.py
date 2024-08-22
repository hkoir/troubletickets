from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from decimal import Decimal, ROUND_DOWN

from django.core.validators import FileExtensionValidator
from django.db.models import Sum, Avg,Count,Q,Case, When, IntegerField,F,Max,DurationField, DecimalField

from vehicle.models import AddVehicleInfo
from generator.models import AddPGInfo
from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES
from account.models import Customer







class MoneyRequisition(models.Model):
    requisition_number = models.CharField(max_length=50,null=True, blank=True, default='None')
    requester = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sending_document = models.FileField(upload_to='Money_sending_documents/', null=True, blank=True)
    money_sending_date = models.DateTimeField(default=timezone.now,null=True, blank=True)
    receiving_status = models.CharField(max_length=50, default='None',null=True, blank=True)
   
    region = models.CharField(max_length=100,choices=REGION_CHOICES,null=True, blank=True)
    zone = models.CharField(max_length=100,choices=ZONE_CHOICES,null=True, blank=True)

    purpose_choices=[
        ('Operations','Operations'),
        ('Adhoc_man','Adhoc_man'),
        ('Adhoc_vehicle','Adhoc_vehicle'),
      
    ]
    purpose = models.CharField(max_length=100,choices=purpose_choices, default="None",null=True, blank=True)
    
    requisition_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,null=True, blank=True)  # Default value added
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,null=True, blank=True)  # Default value added

    supporting_documents = models.FileField(upload_to='supporting_documents/', null=True, blank=True)
    
    APPROVAL_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),  # Corrected 'approved' to 'Approved'
        ('REJECTED', 'Rejected'),
    ]
    approval_status = models.CharField(max_length=50, choices=APPROVAL_STATUS_CHOICES, default='PENDING',null=True, blank=True)
         
    level1_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='level1_approval_histories', null=True, blank=True)
    level2_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='level2_approval_histories', null=True, blank=True)
    level3_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='level3_approval_histories', null=True, blank=True)
    
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








class SummaryExpenses(models.Model):
    region = models.CharField(max_length=100,choices=REGION_CHOICES,null=True, blank=True)
    zone = models.CharField(max_length=100,choices=ZONE_CHOICES,null=True, blank=True)
   
    balance_from_previous_month = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_amount_received = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    office_expenses = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    local_expenses = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    on_demand_vehicle_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    adhoc_PGR_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    dgow_vehicle_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    dgow_run_fuel_cost_cash = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    pm_vehicle_fuel_cost_cash = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cm_vehicle_fuel_cost_cash = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    pgrun_fuel_cost_cash = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    pgrun_fuel_cost_pump = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    site_pm_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    optima_billable = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    optima_non_billable = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    office_rent = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    others = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    advance_due = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_zone_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    balance_forward = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    this_month_cash = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_tt = models.IntegerField()
    total_run_hour = models.DurationField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.total_zone_cost = (
            (self.office_expenses or Decimal(0)) +
            (self.local_expenses or Decimal(0)) +
            (self.on_demand_vehicle_cost or Decimal(0)) +
            (self.adhoc_PGR_cost or Decimal(0)) +
            (self.dgow_run_fuel_cost_cash or Decimal(0)) +
            (self.dgow_vehicle_cost or Decimal(0)) +
            (self.pm_vehicle_fuel_cost_cash or Decimal(0)) +
            (self.cm_vehicle_fuel_cost_cash or Decimal(0)) +
            (self.pgrun_fuel_cost_cash or Decimal(0)) +
            (self.pgrun_fuel_cost_pump or Decimal(0)) +
            (self.site_pm_cost or Decimal(0)) +
            (self.optima_billable or Decimal(0)) +
            (self.optima_non_billable or Decimal(0)) +
            (self.office_rent or Decimal(0)) +
            (self.advance_due or Decimal(0))
        )

        previous_record = SummaryExpenses.objects.filter(zone=self.zone, created_at__lt=self.created_at).order_by('-created_at').first()

        if previous_record:
            self.balance_from_previous_month = previous_record.balance_forward or Decimal(0)
        else:
            self.balance_from_previous_month = Decimal(0)

        if self.total_amount_received is not None:
            self.balance_forward = self.balance_from_previous_month + self.total_amount_received - self.total_zone_cost
            self.this_month_cash = self.total_amount_received + self.balance_from_previous_month
        else:
            self.balance_forward = self.balance_from_previous_month - self.total_zone_cost     

        super().save(*args, **kwargs)

        next_record = SummaryExpenses.objects.filter(zone=self.zone, created_at__gt=self.created_at).order_by('created_at').first()
        if next_record:
            next_record.balance_from_previous_month = self.balance_forward
            next_record.save(update_fields=['balance_from_previous_month'])




class DailyExpenseRequisition(models.Model):
    expense_requisition_number = models.CharField(max_length=50, default='None')
    expense_requester = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sending_document = models.FileField(upload_to='expense_sending_documents/', null=True, blank=True)
    money_sending_date = models.DateTimeField(default=timezone.now,null=True, blank=True)
    expense_requester_mobile = models.IntegerField(null=True, blank=True)

    receiving_status = models.CharField(max_length=50, default='None')
   
    region = models.CharField(max_length=100,choices=REGION_CHOICES,null=True, blank=True)
    zone = models.CharField(max_length=100,choices=ZONE_CHOICES,null=True, blank=True)
    mp = models.CharField(max_length=100,choices=MP_CHOICES,null=True, blank=True)

    expense_requisition_choices=[
        ('local_conveyance','local_conveyance'),
        ('pg_carrying_cost','pg_carrying-cost'),
        ('night_bill','night_bill'),
        ('pg_local_fuel_purchase','pg_local_fuel_purchase'),
        ('vehicle_local_fuel_purchase','vehicle_local_fuel_purchase'),
        ('toll','toll'),
        ('food','food'),
        ('item_purchase','item_purchase'),
        ('field_advance','field_advance'),
        ('others','others')   

    ]

    purpose = models.CharField(max_length=100,choices=expense_requisition_choices)
    pgnumber = models.ForeignKey(AddPGInfo,related_name='pg_daily_expense',null=True,blank=True, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(AddVehicleInfo,related_name="vehicle_daily_expense",null=True,blank=True, on_delete=models.CASCADE)
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # New field for the approved amount
    supporting_documents = models.FileField(upload_to='expenses_supporting_documents/', null=True, blank=True)
    
    from_address = models.TextField(max_length=100,null=True, blank=True,default='None')
    to_address = models.TextField(max_length=100,null=True, blank=True,default='None')

    mode_travel_choices =[
        ('CNG_reserve','CNG_reserve'),
         ('Bike','Bike'),
        ('BUS','BUS'),
        ('Riskshaw','Riskshaw'),
        ('CNG_share','CNG_share'),
        ('Tempu','Tempu'),
        ('others','others'),
    ]
    mode_travel = models.CharField(max_length=100,choices=mode_travel_choices,null=True, blank=True,default='None')
    description = models.TextField(max_length=100,default='None',null=True, blank=True,)
    requisition_amount = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    
    APPROVAL_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('Approved', 'approved'),       
        ('REJECTED', 'Rejected'),
    ]
    approval_status=models.CharField(max_length=50,choices=APPROVAL_STATUS_CHOICES,default='Pending')
         
    level1_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='expense_level1_approval_histories', null=True, blank=True)
    level2_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='expense_level2_approval_histories', null=True, blank=True)
    level3_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='expense_level3_approval_histories', null=True, blank=True)
    
    level1_approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='PENDING')
    level2_approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='PENDING')
    level3_approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='PENDING')
    
    level1_comments = models.TextField(blank=True)
    level2_comments = models.TextField(blank=True)
    level3_comments = models.TextField(blank=True) 

    level1_approval_date = models.DateTimeField(null=True, blank=True)
    level2_approval_date = models.DateTimeField(null=True, blank=True)
    level3_approval_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)




class AdhocRequisition(models.Model):
    adhoc_requisition_number = models.CharField(max_length=50, default='None')
    adhoc_requester = models.ForeignKey(Customer, on_delete=models.CASCADE)   
    receiving_status = models.CharField(max_length=50, default='None')
    sending_document = models.FileField(upload_to='Adhoc_money_sending_documents/', null=True, blank=True)
    money_sending_date = models.DateTimeField(default=timezone.now,null=True, blank=True)
    region = models.CharField(max_length=100,choices=REGION_CHOICES,null=True, blank=True)
    zone = models.CharField(max_length=100,choices=ZONE_CHOICES,null=True, blank=True)
    no_of_adhoc_man_day = models.IntegerField(null=True,blank=True)
    no_of_adhoc_vehicle_day = models.IntegerField(null=True,blank=True)
   
    purpose = models.TextField(null=True, blank=True)
    supporting_documents = models.FileField(upload_to='adhoc_supporting_documents/', null=True, blank=True)

    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # New field for the approved amount
          
    requisition_amount = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    
    APPROVAL_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('Approved', 'approved'),       
        ('REJECTED', 'Rejected'),
    ]
    approval_status=models.CharField(max_length=50,choices=APPROVAL_STATUS_CHOICES,default='Pending')
         
    level1_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='adhoc_level1_approval_histories', null=True, blank=True)
    level2_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='adhoc_level2_approval_histories', null=True, blank=True)
    level3_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='adhoc_level3_approval_histories', null=True, blank=True)
    
    level1_approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='PENDING')
    level2_approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='PENDING')
    level3_approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='PENDING')
    
    level1_comments = models.TextField(blank=True)
    level2_comments = models.TextField(blank=True)
    level3_comments = models.TextField(blank=True)
 

    level1_approval_date = models.DateTimeField(null=True, blank=True)
    level2_approval_date = models.DateTimeField(null=True, blank=True)
    level3_approval_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)


