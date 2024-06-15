from django.contrib import admin

from .models import AddVehicleInfo,FuelRefill,Vehiclefault,VehicleRentalCost,VehicleRuniningData



admin.site.register(AddVehicleInfo)
admin.site.register(FuelRefill)
admin.site.register(Vehiclefault)
admin.site.register(VehicleRentalCost)
admin.site.register(VehicleRuniningData)

