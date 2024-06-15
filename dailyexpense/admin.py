from django.contrib import admin

from .models import MoneyRequisition,SummaryExpenses,DailyExpenseRequisition



admin.site.register(MoneyRequisition)
admin.site.register(SummaryExpenses)
admin.site.register(DailyExpenseRequisition)








