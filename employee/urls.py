from django.urls import path
from . import views

app_name = 'employee'

urlpatterns = [  
      path('', views.view_employee, name='view_employee'),
      path('add_employee/', views.add_employee, name='add_employee'),
      path('view_attendance/', views.view_attendance, name='view_attendance'),
      path('attendance_input/', views.attendance_input, name='attendance_input'),
      path('update_attendance/<int:employee_id>/', views.update_attendance, name='update_attendance'),
      path('update_employee/<int:employee_id>/', views.update_employee, name='update_employee'),
      path('delete_employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),
     
     
      path('create_salary/', views.create_salary, name='create_salary'),
      path('download_salary/', views.download_salary, name='download_salary'),

      path('view_employee_changes/', views.view_employee_changes, name='view_employee_changes'),
      path('download_employee_changes/', views.download_employee_changes, name='download_employee_changes'),

      path('view_employee_changes_single/<int:employee_id>/', views.view_employee_changes_single, name='view_employee_changes_single'),
      path('generate_pay_slip/<int:employee_id>/', views.generate_pay_slip, name='generate_pay_slip'),
    
      path('generate_salary_certificate/<int:employee_id>/', views.generate_salary_certificate, name='generate_salary_certificate'),
      path('generate_experience_certificate/<int:employee_id>/', views.generate_experience_certificate, name='generate_experience_certificate'),


      path('create_resource/', views.create_resource, name='create_resource'),
      path('view_resource/', views.view_resource, name='view_resource'),
      path('view_resource_summary/', views.view_resource_summary, name='view_resource_summary'),
      path('update_resource/<int:resource_id>/', views.update_resource, name='update_resource'),

      path('human_resource_management/', views.human_resource_management, name='human_resource_management'),
]
