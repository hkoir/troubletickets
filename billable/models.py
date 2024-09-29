from django.db import models

from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES

from multiselectfield import MultiSelectField
from django.utils import timezone

from account.models import Customer



class ChatMessage(models.Model):
    ticket_id = models.CharField(max_length=100)
    sender = models.CharField(max_length=100)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class CivilPower(models.Model): 
    region = models.CharField(max_length=50,choices= REGION_CHOICES)
    zone = models.CharField(max_length=50,choices=ZONE_CHOICES)  
    requisition_number = models.CharField(max_length=50,null=True, blank=True, default='None')
    requester = models.ForeignKey(Customer, on_delete=models.CASCADE,null=True)
    task_name_choices = [
        ('single_phase_meter_change','single_phase_meter_change'),
        ('three_phase_meter_change','three_phase_meter_change'),
        ('5kva_transformer_change','5kva_transformer_change'),
        ('10kva_transformer_change','10kva_transformer_change'),
        ('transformer_protection','transformer_protection'),
        ('DG_repiar','DG_repair'),
        ('others','others')
    ]
    task_name = models.CharField(max_length=50,choices=task_name_choices, null=True, blank=True)
    task_description = models.TextField(null=True,blank=True)
    qty = models.IntegerField(null=True,blank=True)
    SOR_rate =  models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
   
    site_code = models.CharField(max_length=50,null=True,blank=True)
    TT_number = models.CharField(max_length=100,null=True,blank=True)
   
    requisition_amount = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    supporting_documents = models.FileField(upload_to='civil_power_supporting_documents/', null=True, blank=True)
    approved_amount = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    actual_cost=models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)

    money_sending_date = models.DateTimeField(default=timezone.now,null=True, blank=True) 
    sending_document = models.FileField(upload_to='Civil_power_Money_sending_documents/', null=True, blank=True)
    receiving_status = models.CharField(max_length=50, default='None',null=True, blank=True)     
   
    APPROVAL_STATUS_CHOICES=[
        ('approved','approved'),
        ('rejected','rejected'),
        ('pending','pending')

    ]
    approval_status = models.CharField(max_length=50,choices=APPROVAL_STATUS_CHOICES,null=True,blank=True)
       
    level1_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='level1_approval_billable', null=True, blank=True)
    level2_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='level2_approval_billable', null=True, blank=True)
    level3_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='level3_approval_billable', null=True, blank=True)
    
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

    TT_open_date =models.DateField(default=timezone.now)
    work_completion_date = models.DateField(null=True, blank=True)
    task_completion_image = models.ImageField(upload_to='billable_tack_completion_image',null=True,blank=True)
    
    task_TT_status_choices=[
        ('open','open'),
        ('closed','closed')
    ]
    TT_status = models.CharField(max_length=100,choices=task_TT_status_choices,null=True,blank=True)

    TT_close_date = models.DateField(null=True,blank=True)   

    remarks = models.TextField(null=True,blank=True)
    created_at = models.DateField(default=timezone.now)


    def __str__(self):
        return self.task_name