from django.urls import path
from . import views

app_name = 'disaster'

urlpatterns = [  
    path('money_requisition/', views. money_requisition, name='money_requisition'),   
    path('requisition_approval/<int:requisition_id>/', views.requisition_approval, name='requisition_approval'),
    path('all_approval_status/', views.all_approval_status, name='all_approval_status'),
    path('mark_received/<int:requisition_id>/', views.mark_received, name='mark_received'),   
    path('download_money_requisition_data/', views.download_money_requisition_data, name='download_money_requisition_data'),
    path('update_money_requisition/<int:requisition_id>/', views.update_money_requisition, name='update_money_requisition'),

    path('disaster_advance_management/', views.disaster_advance_management, name='disaster_advance_management'),
  
]
