# dailyexpense/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import AddPGInfo
from employee.models import Resource
import logging

logger = logging.getLogger('myapp')

@receiver(post_save, sender=AddPGInfo)
@receiver(post_delete, sender=AddPGInfo)
def update_resource_pg_counts(sender, instance, **kwargs):
    logger.info(f'Signal triggered for AddPGInfo with id {instance.id}')
    
    # Ensure you're using the correct region, zone, and mp instances or IDs
    resource = Resource.objects.filter(region=instance.region, zone=instance.zone, mp=instance.mp).first()
    
    if resource:
        good_pg_count = AddPGInfo.objects.filter(region=resource.region, zone=resource.zone, mp=resource.mp, PG_status='good').count()
        faulty_pg_count = AddPGInfo.objects.filter(region=resource.region, zone=resource.zone, mp=resource.mp, PG_status='faulty').count()

        resource.num_of_good_PG = good_pg_count
        resource.num_of_faulty_PG = faulty_pg_count
        resource.save()