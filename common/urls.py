from django.urls import path
from . import views


app_name = 'common'



urlpatterns = [   
     path('operational_resource_management/', views.operational_resource_management, name='operational_resource_management'),   
   
    path('create_fuel_pump_database/', views.create_fuel_pump_database, name='create_fuel_pump_database'), 
    path('view_fuel_pump/', views.view_fuel_pump, name='view_fuel_pump'), 
    path('update_fuel_pump_database/<int:pump_id>/', views.update_fuel_pump_database, name='update_fuel_pump_database'), 
   
     ## PGR database #######################################################################
     path('create_pgr/', views.create_pgr, name='create_pgr'), 
     path('create_pgtl/', views.create_pgtl, name='create_pgtl'), 
     path('view_pgr_database/', views.view_pgr_database, name='view_pgr_database'), 
     path('update_pgr_database/<int:pgr_id>/', views.update_pgr_database, name='update_pgr_database'),
     path('update_pgtl_database/<int:pgtl_id>/', views.update_pgtl_database, name='update_pgtl_database'),  
     path('pgr_summary/', views.pgr_summary_view, name='pgr_summary'), 
     path('upload-pgr-excel/', views.upload_pgr_excel, name='upload_pgr_excel'),   

     path('add_notice/', views.add_notice, name='add_notice'), 
     path('view_notices/', views.view_notices, name='view_notices'),      

     path('fuel_by_pump/', views.fuel_by_pump, name='fuel_by_pump'),   
     path('datewise_fuel_withdraw/', views.datewise_fuel_withdraw, name='datewise_fuel_withdraw'),   

     path('fuel_pump_payment/', views.fuel_pump_payment, name='fuel_pump_payment'),  
     path('view_pump_payment_history/<int:pump_id>/', views.view_pump_payment_history, name='view_pump_payment_history'),  
 
      path('all_expenditure/', views.all_expenditure, name='all_expenditure'),  

]

