from django.contrib import admin



from .models import AdhocAttendance,AdhocPayment,AdhocManRequisition



admin.site.register(AdhocManRequisition)
admin.site.register(AdhocAttendance)
admin.site.register(AdhocPayment)
