from django.contrib import admin

from .models import AddPGInfo,PGFaultRecord,PGFuelRefill,GeneratorService



admin.site.register(AddPGInfo)
admin.site.register(PGFaultRecord)
admin.site.register(PGFuelRefill)
admin.site.register(GeneratorService)


