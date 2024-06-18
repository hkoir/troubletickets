from django.urls import path
from . import views


app_name = 'common'



urlpatterns = [   
     
    path('create_fuel_pump_database/', views.create_fuel_pump_database, name='create_fuel_pump_database'), 
    path('operational_resource_management/', views.operational_resource_management, name='operational_resource_management'),   

       ## PGR database #######################################################################
     path('create_pgr/', views.create_pgr, name='create_pgr'), 
     path('view_pgr_database/', views.view_pgr_database, name='view_pgr_database'), 
     path('update_pgr_database/<int:pgr_id>/', views.update_pgr_database, name='update_pgr_database'), 
     path('pgr_summary/', views.pgr_summary_view, name='pgr_summary'), 
     path('upload-pgr-excel/', views.upload_pgr_excel, name='upload_pgr_excel'),        

]

