from django.urls import path
from . import views


app_name = 'adhocman'



urlpatterns = [   
    path('create_adhoc_requisition/', views.create_adhoc_requisition, name='create_adhoc_requisition'),

    path('adhoc_approval_status/', views.adhoc_approval_status, name='adhoc_approval_status'), 
    path('adhoc_approval_status2/', views.adhoc_approval_status2, name='adhoc_approval_status2'), 
    path('adhoc_management_approval/<int:requisition_id>/', views.adhoc_management_approval, name='adhoc_management_approval'),
    path('adhoc_management_approval2/<int:requisition_id>/', views.adhoc_management_approval2, name='adhoc_management_approval2'),
    path('download_adhoc_requisition_data/', views.download_adhoc_requisition_data, name='download_adhoc_requisition_data'),    
    path('adhoc_management_dashboard/', views.adhoc_management_dashboard, name='adhoc_management_dashboard'),  


    path('adhoc_intime/', views.adhoc_intime, name='adhoc_intime'),  
    path('fetch_requisitions/<int:pgr_id>/', views.fetch_requisitions, name='fetch_requisitions'),
    path('adhoc_outtime/<int:attendance_id>/', views.adhoc_outtime, name='adhoc_outtime'),  
    path('adhoc_outtime2/<int:attendance_id>/', views.adhoc_outtime2, name='adhoc_outtime2'),    
    path('view_adhoc_attendance/', views.view_adhoc_attendance, name='view_adhoc_attendance'),

    path('view_adhoc_attendance2/', views.view_adhoc_attendance2, name='view_adhoc_attendance2'),
    
    path('create_adhoc_payment/<int:adhoc_attendance_id>/', views.create_adhoc_payment, name='create_adhoc_payment'), 
    path('create_adhoc_payment_common/', views.create_adhoc_payment_common, name='create_adhoc_payment_common'),   
     
    path('adhoc_summary_view/', views.adhoc_summary_view, name='adhoc_summary_view'),           
    path('adhoc_pgr_grand_summary/', views.adhoc_pgr_grand_summary, name='adhoc_pgr_grand_summary'), 

    path('pay_pgr_by_name/', views.pay_pgr_by_name, name='pay_pgr_by_name'),  
    path('single_adhoc_payment_view/<int:payment_id>/', views.single_adhoc_payment_view, name='single_adhoc_payment_view'),        
      
         
      
       
   
       
   
]

