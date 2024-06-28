from django.urls import path
from . import views


app_name = 'dailyexpense'



urlpatterns = [   
    path('money_requisition/', views. money_requisition, name='money_requisition'),   
    path('requisition_approval/<int:requisition_id>/', views.requisition_approval, name='requisition_approval'),
    path('all_approval_status/', views.all_approval_status, name='all_approval_status'),
    path('mark_received/<int:requisition_id>/', views.mark_received, name='mark_received'),   
    path('download_money_requisition_data/', views.download_money_requisition_data, name='download_money_requisition_data'),
    path('update_money_requisition/<int:requisition_id>/', views.update_money_requisition, name='update_money_requisition'),

    path('create_expense_requisition/', views.create_expense_requisition, name='create_expense_requisition'),   
    path('expense_requisition_approval/<int:expense_requisition_id>/', views.expense_requisition_approval, name='expense_requisition_approval'),
    path('expense_approval_status/', views.expense_approval_status, name='expense_approval_status'),
    path('expense_received_mark/<int:requisition_id>/', views.expense_received_mark, name='expense_received_mark'),
    path('download_expense_requisition_data/', views.download_expense_requisition_data, name='download_expense_requisition_data'),
    path('daily_expense_summary/', views.daily_expense_summary, name='daily_expense_summary'),
   
    path('summary_expenses_form_view/', views.summary_expenses_form_view, name='summary_expenses_form_view'),
    path('zone_wise_expenses_view/', views.zone_wise_expenses_view, name='zone_wise_expenses_view'),
   path('zone_wise_expenses_view2/', views.zone_wise_expenses_view2, name='zone_wise_expenses_view2'),
    path('update_summary_expenses/<int:summary_expenses_id>/', views.update_summary_expenses, name='update_summary_expenses'),
    path('expense_advance_management/', views.expense_advance_management, name='expense_advance_management'),
  
   
    path('common_search/', views.common_search, name='common_search'),

      
    path('create_adhoc_requisition/', views.create_adhoc_requisition, name='create_adhoc_requisition'),   
    path('adhoc_approval_status/', views.adhoc_approval_status, name='adhoc_approval_status'), 
    path('adhoc_requisition_approval/<int:adhoc_requisition_id>/', views.adhoc_requisition_approval, name='adhoc_requisition_approval'),   
   
    path('adhoc_expense_received_mark/<int:requisition_id>/', views.adhoc_expense_received_mark, name='adhoc_expense_received_mark'),
    path('download_adhoc_requisition_data/', views.download_adhoc_requisition_data, name='download_adhoc_requisition_data'),
]

