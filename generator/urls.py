from django.urls import path
from . import views


app_name = 'generator'



urlpatterns = [   
   
    path('create_pg/', views.create_pg, name='create_pg'),
    path('view_pg_info/', views.view_pg_info, name='view_pg_info'),       
    path('add_pg_fuel/', views.add_pg_fuel, name='add_pg_fuel'),
    path('view_pg_fuel/', views.view_pg_fuel, name='view_pg_fuel'),
    path('view_pg_details_fuel/', views.view_pg_details_fuel, name='view_pg_details_fuel'),
    
    path('pg_summary_report_by_PG/', views.pg_summary_report_by_PG, name='pg_summary_report_by_PG'),
    path('pg_summary_report_by_zone/', views.pg_summary_report_by_zone, name='pg_summary_report_by_zone'),
    path('pg_management/', views.pg_management, name='pg_management'),

    path('update_pg_databaset/<str:pg_PGNumber>/', views.update_pg_database, name='update_pg_database'),
    path('update_pg_status/<str:pg_PGNumber>/', views.update_pg_status, name='update_pg_status'),
    path('faulty_pg_report/', views.faulty_pg_report, name='faulty_pg_report'),

    path('create_pg_fault_record/', views.create_pg_fault_record, name='create_pg_fault_record'),
    path('update_pg_fault_record/<int:pg_id>/', views.update_pg_fault_record, name='update_pg_fault_record'),
    path('view_pg_fault/', views.view_pg_fault, name='view_pg_fault'),
    path('view_pg_details_fault/', views.view_pg_details_fault, name='view_pg_details_fault'),

    path('vendorwise_pg_summary/', views.vendorwise_pg_summary, name='vendorwise_pg_summary'),

    path('create_gen_service/', views.create_gen_service, name='create_gen_service'),
    path('view_gen_service/', views.view_gen_service, name='view_gen_service'),
  

            
]

