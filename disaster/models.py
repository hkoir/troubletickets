from django.db import models
from account.models import Customer
from django.utils import timezone
from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES




class DisasterMoneyRequisition(models.Model):
    requisition_number = models.CharField(max_length=50,null=True, blank=True, default='None')
    requester = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sending_document = models.FileField(upload_to='disaster_Money_sending_documents/', null=True, blank=True)
    money_sending_date = models.DateTimeField(default=timezone.now,null=True, blank=True)
    receiving_status = models.CharField(max_length=50, default='None',null=True, blank=True)
   
    region = models.CharField(max_length=100,choices=REGION_CHOICES,null=True, blank=True)
    zone = models.CharField(max_length=100,choices=ZONE_CHOICES,null=True, blank=True)

    purpose_choices=[
        ('PG_fuel','PG_fuel'),
        ('vehicle_fuel','vehicle_fuel'),
        ('adhoc_man','adhoc_man'),
        ('adhoc_vehicle','adhoc_vehicle'),
        ('others','others')
    ]
    purpose = models.CharField(max_length=100,choices=purpose_choices, default="None",null=True, blank=True)
    
    requisition_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,null=True, blank=True)  # Default value added
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,null=True, blank=True)  # Default value added

    supporting_documents = models.FileField(upload_to='supporting_document_disaster/', null=True, blank=True)
    
    APPROVAL_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),  # Corrected 'approved' to 'Approved'
        ('REJECTED', 'Rejected'),
    ]
    approval_status = models.CharField(max_length=50, choices=APPROVAL_STATUS_CHOICES, default='PENDING',null=True, blank=True)
         
    level1_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='level1_approval_disaster', null=True, blank=True)
    level2_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='level2_approval_disaster', null=True, blank=True)
    level3_approver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='level3_approval_disaster', null=True, blank=True)
    
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

