from django.contrib import admin

from .models import AddPGInfo,PGFaultRecord,PGFuelRefill,Region,Zone,MP



admin.site.register(AddPGInfo)
admin.site.register(PGFaultRecord)
admin.site.register(PGFuelRefill)


admin.site.register(Region)
admin.site.register(Zone)
admin.site.register(MP)
