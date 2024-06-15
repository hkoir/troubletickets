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

    path('vehicle_detail/<int:vehicle_id>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicle_run_details/<str:vehicle_reg_number>/', views.vehicle_run_details, name='vehicle_run_details'),
    
    path('vehicle_summary_report/', views.vehicle_summary_report, name='vehicle_summary_report'),        
    path('management_summary_report/', views.management_summary_report, name='management_summary_report'),
   
    path('vehicle_overtime_calc/', views.vehicle_overtime_calc, name='vehicle_overtime_calc'),   
    path('vehicle_grand_summary/', views.vehicle_grand_summary, name='vehicle_grand_summary'),
    path('fleet_management/', views.fleet_management, name='fleet_management'),
      

]

