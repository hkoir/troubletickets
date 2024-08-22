from django.contrib import admin

from .models import AddVehicleInfo,FuelRefill,Vehiclefault,VehicleRentalCost,VehicleRuniningData
from.models import AdhocVehicleAttendance,AdhocVehiclePayment,AdhocVehicleRequisition


admin.site.register(AddVehicleInfo)
admin.site.register(FuelRefill)
admin.site.register(Vehiclefault)
admin.site.register(VehicleRentalCost)
admin.site.register(VehicleRuniningData)

admin.site.register(AdhocVehicleRequisition)
admin.site.register(AdhocVehicleAttendance)
admin.site.register(AdhocVehiclePayment)

