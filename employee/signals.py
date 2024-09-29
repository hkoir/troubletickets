# employee/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import AddVehicleInfo, OperationalUser, Resource

@receiver([post_save, post_delete], sender=AddVehicleInfo)
@receiver([post_save, post_delete], sender=OperationalUser)
def update_resource_on_change(sender, instance, **kwargs):
    resource = Resource.objects.filter(
        region=instance.region,
        zone=instance.zone,
        mp=instance.mp
    ).first()

    if resource:
        resource.save()  # This will trigger your custom save logic in Resource model
