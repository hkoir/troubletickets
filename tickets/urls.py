from django.urls import path
from . import views

app_name = 'tickets'



urlpatterns = [
     path('', views.dash_board, name='dash_board'),

     path('create_ticket_edotco/', views.create_ticket_edotco, name='create_ticket_edotco'), 
     path('parent_ticket_status_update/<int:ticket_id>/',views.parent_ticket_status_update, name='parent_ticket_status_update'),
        
     path('create_child_ticket/<int:parent_ticket_id>/', views.create_child_ticket, name='create_child_ticket'),
     path('create_child_ticket_mobile/<int:parent_ticket_id>/', views.create_child_ticket_mobile, name='create_child_ticket_mobile'),
     path('view_all_parent_tickets_with_children/', views.view_all_parent_tickets_with_children, name='view_all_parent_tickets_with_children'),
     path('view_child_tickets/<int:parent_ticket_id>/', views.view_child_tickets, name='view_child_tickets'),
     path('view_child_ticket_mobile/<int:parent_ticket_id>/', views.view_child_ticket_mobile, name='view_child_ticket_mobile'),
     path('update_child_ticket_data/', views.UpdateChildTicketData.as_view(), name='update_child_ticket_data'),
       
     path('view_all_parent_tickets_with_children_external/', views.view_all_parent_tickets_with_children_external, name='view_all_parent_tickets_with_children_external'),
     path('view_child_tickets_external/<int:parent_ticket_id>/', views.view_child_tickets_external, name='view_child_tickets_external'),
     path('view_child_tickets_external_mobile/<int:parent_ticket_id>/', views.view_child_tickets_external_mobile, name='view_child_tickets_external_mobile'),
     path('update_child_ticket_data_external/', views.UpdateChildTicketDataExternal.as_view(), name='update_child_ticket_data_external'),
    
     path('view_tt_edotco/', views.view_tt_edotco, name='view_tt_edotco'),  
     path('view_tt_start_stop/', views.view_tt_start_stop, name='view_tt_start_stop'), 
     path('view_tt_disaster/', views.view_tt_disaster, name='view_tt_disaster'),  
     path('update_ticket_edotco/<int:ticket_id>/', views.update_ticket_edotco, name='update_ticket_edotco'),
     path('delete_tt_edotco/<int:ticket_id>/', views.delete_ticket_edotco, name='delete_ticket_edotco'), 
    
     path('chat/<str:ticket_id>/', views.chat, name='chat'),     
    
     path('summary_report_view/', views.summary_report_view, name='summary_report_view'), 
     path('summary_report_view_customerwise/', views.summary_report_view_customerwise, name='summary_report_view_customerwise'), 
     path('summary_report_view_region/', views.summary_report_view_region, name='summary_report_view_region'),
     path('summary_report_view_hourly/', views.summary_report_view_hourly, name='summary_report_view_hourly'),
     path('mp_report_view/', views.mp_report_view, name='mp_report_view'), 
     path('zone_report_view/', views.zone_report_view, name='zone_report_view'),  
 
     path('zone_wise_tt_run_hour_trend_summary/', views.aggregated_tt_run_hour_trend_summary, name='zone_wise_tt_run_hour_trend_summary'),
     path('zone_wise_tt_run_hour_trend/', views.aggregated_tt_run_hour_trend, name='zone_wise_tt_run_hour_trend'),
     path('zone_wise_tt_run_hour_trend2/', views.individual_tt_run_hour_trend, name='zone_wise_tt_run_hour_trend2'),
     path('datewise_summary_edotco/', views.datewise_summary_edotco, name='datewise_summary_edotco'),
   

     path('search_all/', views.search_all, name='search_all'),
     path('tt_management/', views.tt_management, name='tt_management'),

      ## API url ##################################################################
    path('eTicket_list_api/', views.eTickets_details_api, name='eTicket_list_api'), 
    path('eTicket_update_api/<int:id>/', views.eTicket_update_api, name='eTicket_update_api'),  
    path('create_child_ticket_api/<int:parent_ticket_id>/', views.create_child_ticket_api, name='create_child_ticket_api'),  
  
    
]
