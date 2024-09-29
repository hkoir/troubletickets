from django.contrib import admin

from .models import fuelPumpPayment,FuelPumpDatabase,PGRdatabase,PGTLdatabase,OperationalUser



admin.site.register(fuelPumpPayment)
admin.site.register(FuelPumpDatabase)
admin.site.register(PGRdatabase)
admin.site.register(PGTLdatabase)
admin.site.register(OperationalUser)

