from django.contrib import admin

from .models import EmployeeModel, AttendanceModel,MonthlySalaryReport,EmployeeRecordChange,Resource



admin.site.register(EmployeeModel)
admin.site.register(AttendanceModel)
admin.site.register(MonthlySalaryReport)
admin.site.register(EmployeeRecordChange)

admin.site.register(Resource)
