from django.urls import path
from . import views

app_name = 'billable'



urlpatterns = [
  
    path('civil_power_requisition/', views. civil_power_requisition, name='civil_power_requisition'),   
   
    path('requisition_approval/<int:requisition_id>/', views.requisition_approval, name='requisition_approval'),    
    path('civil_power_approval_status/', views.civil_power_approval_status, name='civil_power_approval_status'),

    path('requisition_approval2/<int:requisition_id>/', views.requisition_approval2, name='requisition_approval2'),    
    path('civil_power_approval_status2/', views.civil_power_approval_status2, name='civil_power_approval_status2'),

    path('billable_dashboard/', views.billable_dashboard, name='billable_dashboard'),
    
    path('mark_received/<int:requisition_id>/', views.mark_received, name='mark_received'),   
    path('download_money_requisition_data/', views.download_money_requisition_data, name='download_money_requisition_data'),
    path('upload_money_sending_doc/<int:requisition_id>/', views.upload_money_sending_doc, name='upload_money_sending_doc'),

   path('update_work/<int:requisition_id>/', views.update_work, name='update_work'),

    path('chat/<str:ticket_id>/', views.chat, name='chat'),    


    
]