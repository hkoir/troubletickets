from django.urls import path
from . import views

app_name = 'vehicle'

urlpatterns = [    
     
    path('create_vehicle/', views.create_vehicle, name='create_vehicle'),
    path('create_vehicle_expenses/', views.create_vehicle_expenses, name='create_vehicle_expenses'),
    path('view_vehicle_travel_data/', views.view_vehicle_travel_data, name='view_vehicle_travel_data'),
    path('view_vehicle_info/', views.view_vehicle_info, name='view_vehicle_info'),
    path('update_vehicle_database/<int:vehicle_id>/', views.update_vehicle_database, name='update_vehicle_database'),
    path('delete_vehicle_database/<int:vehicle_id>/', views.delete_vehicle_database, name='delete_vehicle_database'),

    path('create_fuel_refill/', views.create_fuel_refill, name='create_fuel_refill'),
    path('view_fuel_refill/', views.view_fuel_refill, name='view_fuel_refill'),
         
    path('create_vehicle_payment/', views.create_vehicle_payment, name='create_vehicle_payment'),
    path('view_vehicle_payment/', views.view_vehicle_payment, name='view_vehicle_payment'),

    path('create_vehicle_fault/', views.create_vehicle_fault, name='create_vehicle_fault'),
    path('view_vehicle_fault/', views.view_vehicle_fault, name='view_vehicle_fault'),
    path('update_vehicle_fault/<int:vehicle_id>/', views.update_vehicle_fault, name='update_vehicle_fault'),

    path('vehicle_detail/<int:vehicle_id>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicle_run_details/<str:vehicle_reg_number>/', views.vehicle_run_details, name='vehicle_run_details'),
    
    path('vehicle_summary_report/', views.vehicle_summary_report, name='vehicle_summary_report'),        
    path('management_summary_report/', views.management_summary_report, name='management_summary_report'),
   
    path('vehicle_overtime_calc/', views.vehicle_overtime_calc, name='vehicle_overtime_calc'),   
    path('vehicle_grand_summary/', views.vehicle_grand_summary, name='vehicle_grand_summary'),
    path('fleet_management/', views.fleet_management, name='fleet_management'),


    ## only for adhoc vehicle management process ###################################################
    path('adhoc_management_dashboard/', views.adhoc_management_dashboard, name='adhoc_management_dashboard'),  
    
    path('create_adhoc_requisition/', views.create_adhoc_requisition, name='create_adhoc_requisition'),
    path('adhoc_approval_status/', views.adhoc_approval_status, name='adhoc_approval_status'), 

     path('adhoc_approval_status2/', views.adhoc_approval_status2, name='adhoc_approval_status2'), 

    path('adhoc_management_approval/<int:requisition_id>/', views.adhoc_management_approval, name='adhoc_management_approval'),

    path('adhoc_management_approval2/<int:requisition_id>/', views.adhoc_management_approval2, name='adhoc_management_approval2'),

    path('download_adhoc_requisition_data/', views.download_adhoc_requisition_data, name='download_adhoc_requisition_data'), 
    path('adhoc_intime/', views.adhoc_intime, name='adhoc_intime'),  
    path('adhoc_outtime/<int:attendance_id>/', views.adhoc_outtime, name='adhoc_outtime'),  
    path('adhoc_outtime2/<int:attendance_id>/', views.adhoc_outtime2, name='adhoc_outtime2'),  
    path('view_adhoc_attendance/', views.view_adhoc_attendance, name='view_adhoc_attendance'),
    path('view_adhoc_attendance2/', views.view_adhoc_attendance2, name='view_adhoc_attendance2'),
    path('create_adhoc_payment/<int:adhoc_attendance_id>/', views.create_adhoc_payment, name='create_adhoc_payment'),  

     path('adhoc_vehicle_payment_common/', views.adhoc_vehicle_payment_common, name='adhoc_vehicle_payment_common'),              
     path('adhoc_summary_view/', views.adhoc_summary_view, name='adhoc_summary_view'),

    path('adhoc_vehicle_grand_summary/', views.adhoc_vehicle_grand_summary, name='adhoc_vehicle_grand_summary'),
    path('zonewise_vehicle/', views.zonewise_vehicle, name='zonewise_vehicle'),        
      

]

