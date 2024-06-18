from django.contrib import admin

from .models import AddPGInfo,PGFaultRecord,PGFuelRefill



admin.site.register(AddPGInfo)
admin.site.register(PGFaultRecord)
admin.site.register(PGFuelRefill)


