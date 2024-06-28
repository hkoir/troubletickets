from django.urls import path
from . import views


app_name = 'adhocman'



urlpatterns = [   
    path('create_adhoc_requisition/', views.create_adhoc_requisition, name='create_adhoc_requisition'),

    path('adhoc_approval_status/', views.adhoc_approval_status, name='adhoc_approval_status'), 
    path('adhoc_management_approval/<int:requisition_id>/', views.adhoc_management_approval, name='adhoc_management_approval'),

    path('download_adhoc_requisition_data/', views.download_adhoc_requisition_data, name='download_adhoc_requisition_data'),    
    path('adhoc_management_dashboard/', views.adhoc_management_dashboard, name='adhoc_management_dashboard'),  


     path('adhoc_intime/', views.adhoc_intime, name='adhoc_intime'),  
     path('adhoc_outtime/<int:attendance_id>/', views.adhoc_outtime, name='adhoc_outtime'),    
     path('view_adhoc_attendance/', views.view_adhoc_attendance, name='view_adhoc_attendance'),
     path('create_adhoc_payment/<int:adhoc_attendance_id>/', views.create_adhoc_payment, name='create_adhoc_payment'),        
      
         
      
       
   
       
   
]

