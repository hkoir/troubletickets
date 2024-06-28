from django.contrib import admin



from .models import AdhocAttendance,AdhocPayment,AdhocRequisition



admin.site.register(AdhocRequisition)
admin.site.register(AdhocAttendance)
admin.site.register(AdhocPayment)
