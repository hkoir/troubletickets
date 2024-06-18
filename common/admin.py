from django.contrib import admin

from .models import fuelPumpPayment,FuelPumpDatabase,PGRdatabase



admin.site.register(fuelPumpPayment)
admin.site.register(FuelPumpDatabase)
admin.site.register(PGRdatabase)

