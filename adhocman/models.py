from django.db import models
from django.utils import timezone
from datetime import datetime
from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES
from tickets.models import eTicket
from common.models import PGRdatabase
from account.models import Customer
from django.contrib import messages

from django.db.models import Sum, Avg,Count,Q,Case, When, IntegerField,F,Max,DurationField, DecimalField


class AdhocRequisition(models.Model): 
    pgr = models.ForeignKey(PGRdatabase, on_delete=models.CASCADE,blank=True,null=True)
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
    num_of_days_applied = models.IntegerField(null=True, blank=True)
    num_of_days_approved= models.IntegerField(null=True, blank=True) 
    requisition_id= models.CharField(max_length=50,null=True, blank=True, default='None')
    requester = models.ForeignKey(Customer,related_name='adhocman',on_delete=models.CASCADE,null=True,blank=True)   
    purpose = models.TextField(null=True,blank=True) 
    requisition_date = models.DateField(default=timezone.now)
    active_status = models.BooleanField(default=False)
    requisition_status_choices=[
        ('active','active'),
        ('expire','expire')
    ]
    requisition_status = models.CharField(max_length=20,choices=requisition_status_choices,null=True,blank=True,default='active')

    APPROVAL_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    approval_status = models.CharField(max_length=50, choices=APPROVAL_STATUS_CHOICES, default='PENDING')
           
    level1_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='level1_approval_adhocman', null=True, blank=True)
    level2_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='level2_approval_adhocman', null=True, blank=True)
    level3_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='level3_approval_adhocman', null=True, blank=True)
    
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
                self.num_of_days_applied = (self.end_date - self.start_date).days

        level1_approved = self.level1_approval_status and self.level1_approval_status.lower() == 'approved'
        level2_approved = self.level2_approval_status and self.level2_approval_status.lower() == 'approved'
        level3_approved = self.level3_approval_status and self.level3_approval_status.lower() == 'approved'

        if level1_approved and level2_approved and level3_approved:
            self.approval_status = 'Approved'
        else:
             self.approval_status = 'Pending'   
                
        super().save(*args, **kwargs)  # Ensure the changes are saved

    def __str__(self):
        return f"Requisition for {self.pgr.name} on {self.requisition_date}"
  




from django.core.exceptions import ValidationError

class AdhocPayment(models.Model):   
    payment_id = models.CharField(max_length=150, null=True, blank=True)
    pgr = models.ForeignKey(PGRdatabase, on_delete=models.CASCADE, null=True, blank=True)   
    adhoc_paid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_mode_choices = [
        ('bikash', 'bikash'),
        ('rocket', 'rocket'),
        ('nagad', 'nagad'),
        ('bank_transfer', 'bank_transfer')
    ]
    payment_mode = models.CharField(max_length=100, choices=payment_mode_choices, null=True, blank=True)
    transaction_id = models.CharField(max_length=50, null=True, blank=True)
    payment_supporting_document = models.ImageField(upload_to='adhoc_man_payment', null=True, blank=True)
    created_at = models.DateField(default=timezone.now)    

    def clean(self):
        if self.pgr is None:
            raise ValidationError('PGR cannot be None.')

    def __str__(self):
        return self.pgr.name if self.pgr else "No PGR Assigned"



class AdhocAttendance(models.Model):
    adhoc_ticket = models.ForeignKey(eTicket, on_delete=models.CASCADE, related_name='adhoc_attendances',null=True,blank=True)
    pgr = models.ForeignKey(PGRdatabase, on_delete=models.CASCADE)
    adhoc_in_date = models.DateField(null=True, blank=True)
    adhoc_in_time = models.TimeField(null=True, blank=True)
    adhoc_out_date = models.DateField(null=True, blank=True)
    adhoc_out_time = models.TimeField(null=True, blank=True)
    adhoc_working_hours = models.FloatField(null=True, blank=True)
    adhoc_pay_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    adhoc_bill_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)    
    adhoc_payment = models.ForeignKey(AdhocPayment, related_name='adhoc_man_payment_ref', on_delete=models.CASCADE, null=True, blank=True)
   
    adhoc_requisition = models.ForeignKey(AdhocRequisition, related_name='adhoc_man_requisition_ref', on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.adhoc_in_date and self.adhoc_in_time:
            if self.adhoc_out_date and self.adhoc_out_time:
                if self.adhoc_requisition:
                    self.adhoc_requisition.active_status = False
                    self.adhoc_requisition.save()
                in_datetime = datetime.combine(self.adhoc_in_date, self.adhoc_in_time)
                out_datetime = datetime.combine(self.adhoc_out_date, self.adhoc_out_time)
                total_seconds = (out_datetime - in_datetime).total_seconds()
                self.adhoc_working_hours = total_seconds / 3600
                
                self.adhoc_bill_amount = self.adhoc_working_hours * float(self.adhoc_pay_rate)
        
        super(AdhocAttendance, self).save(*args, **kwargs)
       
    def get_active_requisition(self):
        if not self.adhoc_in_date:
            return None
        try:
            requisition = AdhocRequisition.objects.get(
                pgr=self.pgr,
                active_status = True,              
                start_date__lte=self.adhoc_in_date,
                end_date__gte=self.adhoc_in_date,
                level1_approval_status='Approved'
            )
            return requisition
        except AdhocRequisition.DoesNotExist:
            return None

    def __str__(self):
        return self.pgr.name

