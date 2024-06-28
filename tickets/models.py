from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_DOWN
from django.db.models import Max,Min,Sum
from decimal import Decimal

from vehicle.models import AddVehicleInfo
from generator.models import AddPGInfo
from generator.models import PGFuelRefill
from common.models import PGRdatabase
from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES



def get_current_time():
    return timezone.now().time()



class ChatMessage(models.Model):
    ticket_id = models.CharField(max_length=100)
    sender = models.CharField(max_length=100)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)



class eTicket(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    region = models.CharField(max_length=100,choices=REGION_CHOICES,null=True,blank=True)
    zone = models.CharField(max_length=100,choices=ZONE_CHOICES,null=True,blank=True)
    mp = models.CharField(max_length=100,choices=MP_CHOICES,null=True,blank=True)
    internal_ticket_number = models.CharField(max_length=50)

    ticket_type_choices=[
        ('normal','normal'),
        ('disaster_support','disaster_support')
    ]
    ticket_type = models.CharField(max_length=100,choices=ticket_type_choices,null=True,blank=True)

    customer_name_choices = [
        ('Edotco', 'Edotco'),
        ('GP', 'GP'),
        ('BanglaLink', 'Banglalink'),
        ('Robi', 'Robi'),
        ('Teletalk', 'Teletalk'),
        ('emergency_support', 'emergency_support')
    ]
    customer_name = models.CharField(max_length=50, null=True, choices=customer_name_choices, blank=True, default='None')
    customer_ticket_ref = models.CharField(max_length=50)
    site_id = models.CharField(max_length=50)
    ticket_origin_date = models.DateField(default=timezone.now)
    ticket_origin_time = models.TimeField(default=get_current_time)

    assigned_to = models.ForeignKey(PGRdatabase, related_name='ticket_PGR', null=True, blank=True, on_delete=models.CASCADE)
    team_leader_name =models.ForeignKey(PGRdatabase, related_name='ticket_PGTL', null=True, blank=True, on_delete=models.CASCADE)
      
    vehicle = models.ForeignKey(AddVehicleInfo,on_delete=models.SET_NULL, null=True, blank=True)
    pgnumber = models.ForeignKey(AddPGInfo, related_name='pgtickets', on_delete=models.SET_NULL, null=True, blank=True)
    pg_fuel_refill = models.ForeignKey(PGFuelRefill, related_name='pg_fuel',default=None,null=True,blank=True, on_delete=models.CASCADE)

    internal_generator_running_hours = models.DurationField(null=True, blank=True)
    internal_calculated_fuel_litre = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
 
    customer_generator_running_hours = models.DurationField(null=True, blank=True)
    customer_calculated_fuel_litre = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)

    TICKET_STATUS_CHOICES = [   
        ('open', 'open'),   
        ('running', 'running'),
        ('onTheWay', 'onTheWay'),
        ('TT_Miss', 'TT_Miss'),
        ('TT_Valid', 'TT_Valid'),
        ('TT_connected', 'TT_connected'),
        ('team_assign', 'team_assign'),
        ('TT_invalid', 'TT_invalid'),
    ]

    ticket_status = models.CharField(max_length=100, null=True, blank=True, choices=TICKET_STATUS_CHOICES, default='open')
    
    fuel_difference = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.internal_generator_running_hours:
            total_hours = self.internal_generator_running_hours.total_seconds() / 3600
            calculated_fuel = Decimal(total_hours * 2.4)
            self.internal_calculated_fuel_litre = calculated_fuel
        else:
            self.internal_calculated_fuel_litre = Decimal(0)

        if self.customer_generator_running_hours:
            total_hours = self.customer_generator_running_hours.total_seconds() / 3600
            calculated_fuel = Decimal(total_hours * 2.4)
            self.customer_calculated_fuel_litre = calculated_fuel
        else:
            self.customer_calculated_fuel_litre = Decimal(0)

        if self.customer_calculated_fuel_litre is not None and self.internal_calculated_fuel_litre is not None:
            self.fuel_difference = self.customer_calculated_fuel_litre - self.internal_calculated_fuel_litre
        else:
            self.fuel_difference = None

        super().save(*args, **kwargs)



class ChildTicket(models.Model):
    parent_ticket = models.ForeignKey(eTicket, on_delete=models.CASCADE, related_name='child_tickets')
    child_ticket_number = models.CharField(max_length=50)
    
    child_internal_generator_start_date = models.DateField(null=True, blank=True, default=timezone.now)
    child_internal_generator_start_time = models.TimeField(null=True, blank=True)
    child_internal_generator_stop_date = models.DateField(null=True, blank=True, default=timezone.now)
    child_internal_generator_stop_time = models.TimeField(null=True, blank=True)
    
    child_internal_generator_running_hours = models.DurationField(null=True, blank=True)
    child_internal_calculated_fuel_litre = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
   
    child_tt_image = models.ImageField(upload_to='child_tt_image/', blank=True, null=True)

    child_external_generator_start_date = models.DateField(null=True, blank=True, default=timezone.now)
    child_external_generator_start_time = models.TimeField(null=True, blank=True)
    child_external_generator_stop_date = models.DateField(null=True, blank=True, default=timezone.now)
    child_external_generator_stop_time = models.TimeField(null=True, blank=True)
   
    child_external_generator_running_hours = models.DurationField(null=True, blank=True)
    child_external_calculated_fuel_litre = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if (self.child_internal_generator_start_date and self.child_internal_generator_stop_date and
            self.child_internal_generator_start_time and self.child_internal_generator_stop_time):
            start_datetime = datetime.combine(self.child_internal_generator_start_date, self.child_internal_generator_start_time)
            stop_datetime = datetime.combine(self.child_internal_generator_stop_date, self.child_internal_generator_stop_time)
            duration_hours = (stop_datetime - start_datetime).total_seconds() / 3600
            self.child_internal_generator_running_hours = timedelta(hours=duration_hours)

        if self.child_internal_generator_running_hours:
            hours = self.child_internal_generator_running_hours.total_seconds() / 3600
            calculated_fuel = Decimal(hours * 2.4)
            self.child_internal_calculated_fuel_litre = calculated_fuel
        else:
            self.child_internal_calculated_fuel_litre = Decimal(0)
        

        if (self.child_external_generator_start_date and self.child_external_generator_stop_date and
            self.child_external_generator_start_time and self.child_external_generator_stop_time):
            start_datetime = datetime.combine(self.child_external_generator_start_date, self.child_external_generator_start_time)
            stop_datetime = datetime.combine(self.child_external_generator_stop_date, self.child_external_generator_stop_time)
            duration_hours = (stop_datetime - start_datetime).total_seconds() / 3600
            self.child_external_generator_running_hours = timedelta(hours=duration_hours)

        if self.child_external_generator_running_hours:
            hours = self.child_external_generator_running_hours.total_seconds() / 3600
            calculated_fuel = Decimal(hours * 2.4)
            self.child_external_calculated_fuel_litre = calculated_fuel
        else:
            self.child_external_calculated_fuel_litre = Decimal(0)

        super().save(*args, **kwargs)
        self.update_parent_ticket()


    def update_parent_ticket(self):
        parent_ticket = self.parent_ticket

        total_running_hours_internal = parent_ticket.child_tickets.aggregate(total_hours=Sum('child_internal_generator_running_hours'))['total_hours']
        parent_ticket.internal_generator_running_hours = total_running_hours_internal
        parent_ticket.save(update_fields=['internal_generator_running_hours'])

        total_calculated_fuel_internal = parent_ticket.child_tickets.aggregate(total_fuel=Sum('child_internal_calculated_fuel_litre'))['total_fuel']
        parent_ticket.internal_calculated_fuel_litre = total_calculated_fuel_internal
        parent_ticket.save(update_fields=['internal_calculated_fuel_litre'])
     
        total_running_hours_external = parent_ticket.child_tickets.aggregate(total_hours=Sum('child_external_generator_running_hours'))['total_hours']
        parent_ticket.customer_generator_running_hours = total_running_hours_external
        parent_ticket.save(update_fields=['customer_generator_running_hours'])

        total_calculated_fuel_external = parent_ticket.child_tickets.aggregate(total_fuel=Sum('child_external_calculated_fuel_litre'))['total_fuel']
        parent_ticket.customer_calculated_fuel_litre = total_calculated_fuel_external
        parent_ticket.save(update_fields=['customer_calculated_fuel_litre'])



class ChildTicketExternal(models.Model):
    parent_ticket = models.ForeignKey(eTicket, on_delete=models.CASCADE, related_name='child_tickets_external')
    child_external_ticket_number = models.CharField(max_length=50)
    child_external_generator_start_date = models.DateField(null=True, blank=True, default=timezone.now)
    child_external_generator_start_time = models.TimeField(null=True, blank=True)
    child_external_generator_stop_date = models.DateField(null=True, blank=True, default=timezone.now)
    child_external_generator_stop_time = models.TimeField(null=True, blank=True)
    child_external_generator_running_hours = models.DurationField(null=True, blank=True)
    child_external_calculated_fuel_litre = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    child_external_tt_image = models.ImageField(upload_to='child_tt_image_external/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if (self.child_external_generator_start_date and self.child_external_generator_stop_date and
            self.child_external_generator_start_time and self.child_external_generator_stop_time):
            start_datetime = datetime.combine(self.child_external_generator_start_date, self.child_external_generator_start_time)
            stop_datetime = datetime.combine(self.child_external_generator_stop_date, self.child_external_generator_stop_time)
            duration_hours = (stop_datetime - start_datetime).total_seconds() / 3600
            self.child_external_generator_running_hours = timedelta(hours=duration_hours)

        if self.child_external_generator_running_hours:
            hours = self.child_external_generator_running_hours.total_seconds() / 3600
            calculated_fuel = Decimal(hours * 2.4)
            self.child_external_calculated_fuel_litre = calculated_fuel
        else:
            self.child_external_calculated_fuel_litre = Decimal(0)

        super().save(*args, **kwargs)

        # Update the parent eTicket's running hours and calculated fuel
        self.update_parent_ticket()

    def update_parent_ticket(self):
        parent_ticket = self.parent_ticket
        total_running_hours = parent_ticket.child_tickets_external.aggregate(total_hours=Sum('child_external_generator_running_hours'))['total_hours']
        parent_ticket.customer_generator_running_hours = total_running_hours
        parent_ticket.save(update_fields=['customer_generator_running_hours'])

        total_calculated_fuel = parent_ticket.child_tickets_external.aggregate(total_fuel=Sum('child_external_calculated_fuel_litre'))['total_fuel']
        parent_ticket.customer_calculated_fuel_litre = total_calculated_fuel
        parent_ticket.save(update_fields=['customer_calculated_fuel_litre'])











