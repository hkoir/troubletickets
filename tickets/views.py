import pandas as pd
from django.http import HttpResponse,JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone
from itertools import groupby
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect,get_object_or_404
from django.db.models import Sum, Avg,Count,Q,Case, When, IntegerField,F,Max,DurationField, DecimalField,FloatField,Prefetch,ExpressionWrapper, DecimalField,Exists, OuterRef
import random,json,uuid,base64,csv

from .serializers import eTicketSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

from .models import eTicket,ChatMessage,ChildTicket,ChildTicketExternal,PGRdatabase
from .forms import CreateTicketFormEdotco,UpdateTicketFormEdotco,ChatForm,SummaryReportForm,MPReportForm,ZoneReportForm,UpdateTicketFormEdotco
from .forms import SummaryReportFormHourly,SummaryReportChartForm,CreateChildTicketForm,TicketStatusUpdateForm

from employee.models import EmployeeModel
from generator.models import AddPGInfo
from account.models import AudioModel

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from collections import defaultdict



@login_required
def dash_board(request):
    audio_files = AudioModel.objects.all()
    return render(request, 'tickets/edotco/dash_board.html',{'audio_files':audio_files})


@login_required
def search_all(request):
    query = request.GET.get('q')
    etickets = eTicket.objects.filter(
        Q(internal_ticket_number__icontains=query) | 
        Q(region__icontains=query) |  
        Q(zone__icontains=query) |    
        Q(mp__icontains=query) |      
        Q(site_id__icontains=query) | 
        Q(ticket_status__icontains=query)
    )
    
    child_tickets = ChildTicket.objects.none()  
    if etickets.exists():
        child_tickets = ChildTicket.objects.filter(parent_ticket__in=etickets)   
    employees = EmployeeModel.objects.filter(
        Q(name__icontains=query) | 
        Q(employee_code__icontains=query) | 
        Q(email__icontains=query) | 
        Q(phone_number__icontains=query) | 
        Q(position__icontains=query) | 
        Q(department__icontains=query)
    )
    return render(request, 'tickets/search_results.html', {
        'employees': employees, 
        'etickets': etickets, 
        'query': query,
        'child_tickets': child_tickets
    })


def generate_unique_ticket_number():   
    random_number = random.randint(100, 999)  
    ticket_number = f'{timezone.now().strftime("%Y%m%d%H%M%S")}{random_number}'
    return ticket_number

def generate_unique_finance_requisition_number2():   
    random_number = random.randint(100000, 999999)  
    ticket_number = f'{timezone.now().strftime("%Y%m%d%H%M%S")}{random_number}'
    return ticket_number

def generate_unique_finance_requisition_number3():
    random_number = random.randint(100000, 999999)
    ticket_number = f'{timezone.now().strftime("%Y%m%d%H%M%S")}{random_number}'
    return str(ticket_number)

def generate_unique_finance_requisition_number():
    random_number = str(random.randint(100000, 999999))
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    ticket_number = f'{timestamp}{random_number}'
    return ticket_number


@login_required
def create_ticket_edotco2(request):
    if request.method == 'POST':
        form = CreateTicketFormEdotco(request.POST)
        if form.is_valid():           
            ticket = form.save(commit=False) 
            ticket.internal_ticket_number = generate_unique_ticket_number() 
            ticket.save()  
            return redirect('tickets:view_tt_edotco') 
        else:
             messages.error(request, " Something went wrong. Please try again carefully")
    else:
        form = CreateTicketFormEdotco()
    return render(request, 'tickets/edotco/create_tt.html', {'form': form})


@login_required
def create_ticket_edotco(request):
    if request.method == 'POST':
        form = CreateTicketFormEdotco(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.internal_ticket_number = generate_unique_ticket_number()
            ticket.save()
            messages.success(request, "Ticket created successfully!")
            return redirect('tickets:view_tt_edotco')
        else:
            messages.error(request, "Something went wrong. Please check the form and try again.")
    else:
        form = CreateTicketFormEdotco()
    return render(request, 'tickets/edotco/create_tt.html', {'form': form})


@login_required
def update_ticket_edotco(request, ticket_id):
    ticket = get_object_or_404(eTicket, id=ticket_id)    
    if request.user.is_authenticated:
        user_role = request.user.manager_level
    else:
        return redirect('account:login')    
    if request.method == 'POST':
        form = UpdateTicketFormEdotco(request.POST, instance=ticket, user_role=user_role)        
        if form.is_valid():
            try:
                with transaction.atomic():
                    updated_ticket = form.save(commit=False)
                    vehicle = form.cleaned_data.get('vehicle')
                    pgnumber = form.cleaned_data.get('pgnumber')                    
                    updated_ticket.vehicle = vehicle if vehicle else None                    
                    if pgnumber:
                        pg_condition = get_object_or_404(AddPGInfo, PGNumber=pgnumber)
                        if pg_condition.PG_status != 'faulty':
                            updated_ticket.pgnumber = pgnumber
                        else:
                            messages.error(request, "This PG is faulty declared. If it has been repaired, please update your PG database first.")
                            return render(request, 'tickets/edotco/update_tt.html', {'form': form})
                    else:
                        updated_ticket.pgnumber = None

                    updated_ticket.save()
                    return redirect('tickets:view_tt_edotco')      
            except IntegrityError:
                form.add_error(None, 'There was an error saving the ticket due to a foreign key constraint failure.')
        else:
             messages.error(request, " Something went wrong. Please try again carefully")
    else:
        form = UpdateTicketFormEdotco(instance=ticket, user_role=user_role)
    return render(request, 'tickets/edotco/update_tt.html', {'form': form})


@login_required
def delete_ticket_edotco(request, ticket_id):
    ticket = get_object_or_404(eTicket, id=ticket_id)
    if request.method == 'POST':
        if request.POST.get('confirm') == 'yes': 
            ticket.delete()
            messages.success(request, 'Ticket deleted successfully.')
            return redirect('tickets:view_tt_edotco')  
        else:
            return redirect('tickets:view_tt_edotco')
    return render(request, 'tickets/edotco/delete_record.html', {'ticket': ticket})


@login_required
def parent_ticket_status_update(request,ticket_id):
    ticket = get_object_or_404(eTicket, id= ticket_id)
    if request.method == 'POST':
        form = TicketStatusUpdateForm(request.POST,instance=ticket)
        if form.is_valid():
            ticket = form.save(commit=False)           
            ticket.save()  
            return redirect('tickets:view_tt_edotco') 
    else:
        initial_data = {
            'ticket_number': ticket.internal_ticket_number,
            'ticket_status': ticket.ticket_status
        }
        form =TicketStatusUpdateForm(instance=ticket,initial = initial_data)    
    return render(request, 'tickets/edotco/create_tt.html', {'form': form,'ticket':ticket})

   
@login_required
def chat(request, ticket_id):
    ticket = get_object_or_404(eTicket, pk=ticket_id)
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket_id = ticket_id
            message.ticket = ticket 
            message.ticket_number = ticket.internal_ticket_number
            message.sender = request.user.name
            message.timestamp = timezone.now()
            message.save()
            return redirect('tickets:chat', ticket_id=ticket_id)
    else:
        form = ChatForm()
    messages = ChatMessage.objects.filter(ticket_id=ticket_id).order_by('timestamp')
    return render(request, 'tickets/edotco/tchat.html', {'ticket': ticket, 'messages': messages, 'form': form})


############### Child ticket start tt#################################################################

@login_required
def create_child_ticket(request, parent_ticket_id):
    parent_ticket = get_object_or_404(eTicket, id=parent_ticket_id)
    ticket_status = parent_ticket.ticket_status
    if request.method == 'POST':
        form = CreateChildTicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.parent_ticket = parent_ticket
            if form.cleaned_data['UploadPicture'] and form.cleaned_data['TakePicture']:
                print('Please select only one option for picture')
                form.add_error('UploadPicture', 'Please select only one option for picture')
                form.add_error('TakePicture', 'Please select only one option for picture')
            elif form.cleaned_data['UploadPicture']:
                ticket.child_tt_image = form.cleaned_data['UploadPicture']
            elif form.cleaned_data['TakePicture']:
                ticket.child_tt_image = form.cleaned_data['TakePicture']
            ticket.child_ticket_number = generate_unique_ticket_number()
            ticket.save()
            parent_ticket.ticket_status = form.cleaned_data.get('ticket_status', parent_ticket.ticket_status)
            parent_ticket.save()
            return redirect('tickets:view_tt_edotco')
    else:
        initial_data = {
            'parent_ticket_number': parent_ticket.internal_ticket_number,
            'ticket_status': ticket_status
        }
        form = CreateChildTicketForm(initial=initial_data)
    return render(request, 'tickets/edotco/create_child_tt.html', {'form': form})



@login_required
def create_child_ticket_mobile(request, parent_ticket_id):
    parent_ticket = get_object_or_404(eTicket, id=parent_ticket_id)
    ticket_status = parent_ticket.ticket_status
    if request.method == 'POST':
        form = CreateChildTicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.parent_ticket = parent_ticket
            if form.cleaned_data['UploadPicture'] and form.cleaned_data['TakePicture']:
                print('Please select only one option for picture')
                form.add_error('UploadPicture', 'Please select only one option for picture')
                form.add_error('TakePicture', 'Please select only one option for picture')
            elif form.cleaned_data['UploadPicture']:
                ticket.child_tt_image = form.cleaned_data['UploadPicture']
            elif form.cleaned_data['TakePicture']:
                ticket.child_tt_image = form.cleaned_data['TakePicture']
            ticket.child_ticket_number = generate_unique_ticket_number()
            ticket.save()
            parent_ticket.ticket_status = form.cleaned_data.get('ticket_status', parent_ticket.ticket_status)
            parent_ticket.save()
            return redirect('tickets:view_tt_start_stop')
    else:
        initial_data = {
            'parent_ticket_number': parent_ticket.internal_ticket_number,
            'ticket_status': ticket_status
            }
        form = CreateChildTicketForm(initial=initial_data)
    return render(request, 'tickets/edotco/create_child_tt.html', {'form': form})


@login_required
def view_child_tickets(request, parent_ticket_id):
    parent_ticket = get_object_or_404(eTicket, pk=parent_ticket_id)  
    child_tickets = parent_ticket.child_tickets.all()
    
    return render(request, 'tickets/edotco/view_child_tickets_single.html', {'parent_ticket': parent_ticket, 'child_tickets': child_tickets})

@login_required
def view_child_ticket_mobile(request, parent_ticket_id):
    parent_ticket = get_object_or_404(eTicket, pk=parent_ticket_id)  
    child_tickets = parent_ticket.child_tickets.all()    
    return render(request,'tickets/edotco/view_child_tickets_single_mobile.html', {'parent_ticket': parent_ticket, 'child_tickets': child_tickets})


################## ajax view to update for PG stop only ################################

@method_decorator(csrf_exempt, name='dispatch')
class UpdateChildTicketData(View):
    def post(self, request):
        try:
            changes = json.loads(request.body)            
            for change in changes:
                child_ticket_id = change.get('id')
                field = change.get('field')
                value = change.get('value')              
                child_ticket = ChildTicket.objects.get(id=child_ticket_id)
                if field in ['child_internal_generator_start_date', 'child_internal_generator_stop_date']:
                    value = datetime.strptime(value, '%Y-%m-%d').date()
                elif field in ['child_internal_generator_start_time', 'child_internal_generator_stop_time']:
                    value = datetime.strptime(value, '%H:%M:%S').time()
                setattr(child_ticket, field, value)
                child_ticket.save()
            return JsonResponse({'message': 'Successfully updated'})
        except ChildTicket.DoesNotExist:
            return JsonResponse({'error': 'Child ticket not found'}, status=404)
        except ValueError as ve:
            print(f'ValueError: {ve}')  # Debugging
            return JsonResponse({'error': 'Invalid date or time format'}, status=400)
        except Exception as e:      
            return JsonResponse({'error': str(e)}, status=400)


@login_required
def view_all_parent_tickets_with_children(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None
    page_obj = None
    form = SummaryReportChartForm(request.GET or {'days': 30})
    parent_tickets = eTicket.objects.all().prefetch_related(
        Prefetch('child_tickets_external', queryset=ChildTicketExternal.objects.all(), to_attr='prefetched_child_tickets_external'),
        Prefetch('child_tickets', queryset=ChildTicket.objects.all(), to_attr='prefetched_child_tickets'),       
    ).order_by('-created_at')
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        if start_date and end_date:
            parent_tickets = parent_tickets.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            parent_tickets = parent_tickets.filter(created_at__range=(start_date, end_date))
        if region:
            parent_tickets = parent_tickets.filter(region=region)
        if zone:
            parent_tickets = parent_tickets.filter(zone=zone)
        if mp:
            parent_tickets = parent_tickets.filter(mp=mp)
    ticket_data = []
    tickets_per_page = 5
    paginator = Paginator(parent_tickets, tickets_per_page)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    if 'download_csv' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="view_ticket.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Parent Ticket Created At', 'Region', 'Zone', 'MP', 'Parent Ticket Number',
            'Child Ticket Number', 'Child Generator Start Date', 'Child Generator Start Time',
            'Child Generator Stop Date', 'Child Generator Stop Time', 'Child Generator Running Hours',
            'Child Calculated Fuel Litre'
        ])
        for ticket in page_obj:
            parent_data = [
                ticket.created_at,
                ticket.region,
                ticket.zone,
                ticket.mp,
                "'" + str(ticket.internal_ticket_number)
            ]
            for child_ticket in ticket.child_tickets.all():
                writer.writerow(parent_data + [
                    "'" + str(child_ticket.child_ticket_number),
                    child_ticket.child_internal_generator_start_date,
                    child_ticket.child_internal_generator_start_time,
                    child_ticket.child_internal_generator_stop_date,
                    child_ticket.child_internal_generator_stop_time,
                    child_ticket.child_internal_generator_running_hours,
                    child_ticket.child_internal_calculated_fuel_litre
                ])
            for child_ticket_external in ticket.child_tickets_external.all():
                writer.writerow(parent_data + [
                    "'" + str(child_ticket_external.child_external_ticket_number),
                    child_ticket_external.child_external_generator_start_date,
                    child_ticket_external.child_external_generator_start_time,
                    child_ticket_external.child_external_generator_stop_date,
                    child_ticket_external.child_external_generator_stop_time,
                    child_ticket_external.child_external_generator_running_hours,
                    child_ticket_external.child_external_calculated_fuel_litre
                ])
        return response
    
    for ticket in page_obj:
        ticket.fuel_difference = ticket.customer_calculated_fuel_litre - ticket.internal_calculated_fuel_litre
        ticket_dict = {}
        ticket_fields = eTicket._meta.get_fields()
        for field in ticket_fields:            
            field_name = field.name
            try:
                field_value = getattr(ticket, field_name)
            except: ObjectDoesNotExist
            ticket_dict[field_name] = field_value
        ticket_data.append(ticket_dict)

    form = SummaryReportChartForm
    return render(request, 'tickets/edotco/view_child_tickets.html', {
        'parent_tickets': parent_tickets,
        'form': form,
        'page_obj': page_obj,
        'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'region': region,
        'zone': zone,
        'mp': mp,
    })



############## child Ticket external start ##############################
@login_required
def view_child_tickets_external(request, parent_ticket_id):
    parent_ticket = get_object_or_404(eTicket, pk=parent_ticket_id)  
    child_tickets = parent_ticket.child_tickets.all()    
    return render(request, 'tickets/external_childticket/view_child_tickets_single.html', {'parent_ticket': parent_ticket, 'child_tickets': child_tickets})

@login_required
def view_child_tickets_external_mobile(request, parent_ticket_id):
    parent_ticket = get_object_or_404(eTicket, pk=parent_ticket_id)  
    child_tickets = parent_ticket.child_tickets.all()    
    return render(request, 'tickets/external_childticket/view_child_tickets_single_mobile.html', {'parent_ticket': parent_ticket, 'child_tickets': child_tickets})



# ajax for updating data for validation/checking
@method_decorator(csrf_exempt, name='dispatch')
class UpdateChildTicketDataExternal(View):
    def post(self, request):
        try:
            changes = json.loads(request.body)            
            for change in changes:
                child_ticket_id = change.get('id')
                field = change.get('field')
                value = change.get('value')          
                child_ticket = ChildTicket.objects.get(id=child_ticket_id)
                if field in ['child_external_generator_start_date', 'child_exernal_generator_stop_date']:
                    value = datetime.strptime(value, '%Y-%m-%d').date()
                elif field in ['child_external_generator_start_time', 'child_external_generator_stop_time']:
                    value = datetime.strptime(value, '%H:%M:%S').time()
                setattr(child_ticket, field, value)
                child_ticket.save()
            return JsonResponse({'message': 'Successfully updated'})
        except ChildTicket.DoesNotExist:
            return JsonResponse({'error': 'Child ticket not found'}, status=404)
        except ValueError as ve:
            print(f'ValueError: {ve}')  # Debugging
            return JsonResponse({'error': 'Invalid date or time format'}, status=400)
        except Exception as e:
            print(f'Error: {e}')  # Debugging
            return JsonResponse({'error': str(e)}, status=400)



@login_required
def view_all_parent_tickets_with_children_external(request):  
    parent_tickets = eTicket.objects.all().prefetch_related('child_tickets_external')
    return render(request, 'tickets/external_childticket/view_child_tickets.html', {'parent_tickets': parent_tickets})



############# parent ticket reporting view start from here ##################################################

@login_required
def view_tt_edotco(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None
    ticket_number=None    
    form = SummaryReportChartForm(request.GET or {'days':60})   
    tickets = eTicket.objects.all()
    tickets = eTicket.objects.annotate(
        has_messages=Exists(
            ChatMessage.objects.filter(ticket_number=OuterRef('internal_ticket_number'))
        )
    ).order_by('-created_at')  
    user = request.user
    user_name = user.employee.name if user.employee else None    
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        ticket_number = form.cleaned_data.get('ticket_number')        
        if start_date and end_date:         
            start_date = timezone.make_aware(start_date) if timezone.is_naive(start_date) else start_date
            end_date = timezone.make_aware(end_date) if timezone.is_naive(end_date) else end_date
            tickets = tickets.filter(created_at__range=(start_date, end_date))
            if region:
                tickets = tickets.filter(region=region)
        elif days:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            tickets = tickets.filter(created_at__range=(start_date, end_date))          
        if region:
            tickets = tickets.filter(region=region)
        if zone:
            tickets = tickets.filter(zone=zone)
        if mp:
            tickets = tickets.filter(mp=mp)
        if ticket_number:
            tickets = tickets.filter(internal_ticket_number=ticket_number)

    ticket_data = []
    tickets_per_page = 10
    paginator = Paginator(tickets, tickets_per_page)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    total_valid_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'TT_Valid')
    total_invalid_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'TT_invalid')
    total_missed_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'TT_Miss')
    total_open_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'open')
    total_running_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'running')
    total_ontheway_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'onTheWay')
    total_connected_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'TT_connected')
    total_assigned_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'team_assign')
    total_ticket = (
        total_valid_ticket + total_invalid_ticket + total_missed_ticket + 
        total_open_ticket + total_running_ticket + total_ontheway_ticket + 
        total_connected_ticket + total_assigned_ticket
    )
    if 'download_csv' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="view_ticket.csv"'
        writer = csv.writer(response)
        writer.writerow(['created_at', 'Region', 'Zone', 'MP', 'Ticket Number'])
        for ticket in page_obj:
            writer.writerow([
                ticket.created_at,
                ticket.region,
                ticket.zone,
                ticket.mp,
                "'" + str(ticket.internal_ticket_number)
                ])

        return response

    for ticket in page_obj:
        ticket.fuel_difference = ticket.customer_calculated_fuel_litre - ticket.internal_calculated_fuel_litre
        ticket_dict = {}
        ticket_fields = eTicket._meta.get_fields()        
        for field in ticket_fields:
            field_name = field.name
            try:
                field_value = getattr(ticket, field_name)
            except ObjectDoesNotExist:
                field_value = None  
            ticket_dict[field_name] = field_value
        ticket_dict['has_messages'] = ticket.has_messages
        ticket_data.append(ticket_dict)
    cleared_form = SummaryReportChartForm()
    return render(request, 'tickets/edotco/view_tt.html', {
        'ticket_data': ticket_data,
        'page_obj': page_obj,
        'form': form,
        'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'region': region,
        'zone': zone,
        'mp': mp,
        'form': cleared_form,
        'total_ticket': total_ticket,
        'total_valid_ticket': total_valid_ticket,
        'total_invalid_ticket': total_invalid_ticket,
        'total_missed_ticket': total_missed_ticket,
        'total_open_ticket': total_open_ticket,
        'total_running_ticket': total_running_ticket,
        'total_ontheway_ticket': total_ontheway_ticket,
        'total_connected_ticket': total_connected_ticket,
        'total_assigned_ticket': total_assigned_ticket,
        
    })



@login_required
def view_tt_start_stop(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None
    ticket_number = None    
    form = SummaryReportChartForm(request.GET or {'days': 20})
    tickets = eTicket.objects.all().order_by('-created_at')
    user = request.user
    user_name = None 
    if user.employee:
        user_name = user.employee.name       
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        ticket_number = form.cleaned_data.get('ticket_number')        
        if start_date and end_date:
            tickets = tickets.filter(created_at__range=(start_date, end_date))
            if region:
                tickets = tickets.filter(region=region)
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            tickets = tickets.filter(created_at__range=(start_date, end_date))          
        if region:
            tickets = tickets.filter(region=region)
        if zone:
            tickets = tickets.filter(zone=zone)
        if mp:
            tickets = tickets.filter(mp=mp)        
        if ticket_number:
            tickets = tickets.filter(internal_ticket_number = ticket_number)              
    ticket_data = []
    tickets_per_page = 10
    paginator = Paginator(tickets, tickets_per_page)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    total_valid_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'TT_Valid')
    total_invalid_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'TT_invalid')
    total_missed_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'TT_Miss')
    total_open_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'open')
    total_running_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'running')
    total_ontheway_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'onTheWay')
    total_connected_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'TT_connected')
    total_assigned_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'team_assign')
    total_ticket = (
        total_valid_ticket + total_invalid_ticket + total_missed_ticket + 
        total_open_ticket + total_running_ticket + total_ontheway_ticket + 
        total_connected_ticket + total_assigned_ticket
    )

    if 'download_csv' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="view_ticket.csv"'
        writer = csv.writer(response)
        writer.writerow(['created_at', 'Region', 'Zone', 'MP', 'Ticket Number'])
        for ticket in page_obj:
            writer.writerow([
                ticket.created_at,
                ticket.region,
                ticket.zone,
                ticket.mp,
                "'" + str(ticket.internal_ticket_number)
            ])

        return response
    for ticket in page_obj:
        ticket.fuel_difference = ticket.customer_calculated_fuel_litre - ticket.internal_calculated_fuel_litre
        ticket_dict = {}
        ticket_fields = eTicket._meta.get_fields()        
        for field in ticket_fields:
            field_name = field.name
            try:
                field_value = getattr(ticket, field_name)
            except ObjectDoesNotExist:
                field_value = None  # Handle missing related object
            ticket_dict[field_name] = field_value
        
        ticket_data.append(ticket_dict)
    cleared_form = SummaryReportChartForm()
    return render(request, 'tickets/edotco/view_tt _start_stop.html', {
        'ticket_data': ticket_data,
        'page_obj': page_obj,
        'form': form,
        'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'region': region,
        'zone': zone,
        'mp': mp,
        'form': cleared_form,
        'total_ticket': total_ticket,
        'total_valid_ticket': total_valid_ticket,
        'total_invalid_ticket': total_invalid_ticket,
        'total_missed_ticket': total_missed_ticket,
        'total_open_ticket': total_open_ticket,
        'total_running_ticket': total_running_ticket,
        'total_ontheway_ticket': total_ontheway_ticket,
        'total_connected_ticket': total_connected_ticket,
        'total_assigned_ticket': total_assigned_ticket
    })





@login_required
def view_tt_disaster(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None    
    form = SummaryReportChartForm(request.GET or {'days': 20})
    tickets = eTicket.objects.filter(ticket_type='disaster_support').order_by('-created_at')
    user = request.user
    user_name = None  
    if user.employee:
        user_name = user.employee.name
        print(user_name)
    else:
        print("User does not have an associated employee.")    
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')        
        if start_date and end_date:
            tickets = tickets.filter(created_at__range=(start_date, end_date))
            if region:
                tickets = tickets.filter(region=region)
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            tickets = tickets.filter(created_at__range=(start_date, end_date))          
        if region:
            tickets = tickets.filter(region=region)
        if zone:
            tickets = tickets.filter(zone=zone)
        if mp:
            tickets = tickets.filter(mp=mp)
    ticket_data = []
    tickets_per_page = 10
    paginator = Paginator(tickets, tickets_per_page)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    total_valid_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'TT_Valid')
    total_invalid_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'TT_invalid')
    total_missed_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'TT_Miss')
    total_open_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'open')
    total_running_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'running')
    total_ontheway_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'onTheWay')
    total_connected_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'TT_connected')
    total_assigned_ticket = sum(1 for ticket in page_obj if ticket.ticket_status == 'team_assign')
    total_ticket = (
        total_valid_ticket + total_invalid_ticket + total_missed_ticket + 
        total_open_ticket + total_running_ticket + total_ontheway_ticket + 
        total_connected_ticket + total_assigned_ticket
    )
    if 'download_csv' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="view_ticket.csv"'
        writer = csv.writer(response)
        writer.writerow(['created_at', 'Region', 'Zone', 'MP', 'Ticket Number'])
        for ticket in page_obj:
            writer.writerow([
                ticket.created_at,
                ticket.region,
                ticket.zone,
                ticket.mp,
                "'" + str(ticket.internal_ticket_number)
            ])

        return response

    for ticket in page_obj:
        ticket.fuel_difference = ticket.customer_calculated_fuel_litre - ticket.internal_calculated_fuel_litre
        ticket_dict = {}
        ticket_fields = eTicket._meta.get_fields()        
        for field in ticket_fields:
            field_name = field.name
            try:
                field_value = getattr(ticket, field_name)
            except ObjectDoesNotExist:
                field_value = None 
            ticket_dict[field_name] = field_value        
        ticket_data.append(ticket_dict)
    cleared_form = SummaryReportChartForm()
    return render(request, 'tickets/edotco/view_tt disaster.html', {
        'ticket_data': ticket_data,
        'page_obj': page_obj,
        'form': form,
        'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'region': region,
        'zone': zone,
        'mp': mp,
        'form': cleared_form,
        'total_ticket': total_ticket,
        'total_valid_ticket': total_valid_ticket,
        'total_invalid_ticket': total_invalid_ticket,
        'total_missed_ticket': total_missed_ticket,
        'total_open_ticket': total_open_ticket,
        'total_running_ticket': total_running_ticket,
        'total_ontheway_ticket': total_ontheway_ticket,
        'total_connected_ticket': total_connected_ticket,
        'total_assigned_ticket': total_assigned_ticket
    })



@login_required
def summary_report_view(request):
    form = SummaryReportForm(request.GET or {'days': 20})
    summary_data = []
    report_date = None
    days = None
    if form.is_valid():
        report_date = form.cleaned_data.get('report_date')
        days = form.cleaned_data.get('days')
        if report_date:
            summary = eTicket.objects.filter(created_at__date=report_date).values('region', 'zone') \
            .annotate(
                    num_tickets=Count('id'),
                    num_closed_tickets=Count('id', filter=Q(ticket_status='closed')),
                    num_valid_tickets=Count('id', filter=Q(ticket_status='TT_Valid')),
                    num_invalid_tickets=Count('id', filter=Q(ticket_status='TT_invalid')),
                    num_miss_tickets=Count('id', filter=Q(ticket_status='TT_Miss')),
                    num_running_tickets=Count('id', filter=Q(ticket_status='running')),
                    num_connected_tickets=Count('id', filter=Q(ticket_status='TT_connected')),
                    num_otw_tickets=Count('id', filter=Q(ticket_status='onTheWay')),
                    num_open_tickets=Count('id', filter=Q(ticket_status='open')),
                    num_team_assign_tickets=Count('id', filter=Q(ticket_status='team_assign')),
                    num_adhoc_PGR=Count('id', filter=Q(assigned_to__PGR_category='adhoc')),
                    num_adhoc_vehicle=Count('id', filter=Q(vehicle__vehicle_rental_type='adhoc')),                    
                   total_hepta_running_hours=ExpressionWrapper(
                    Sum(F('internal_generator_running_hours')) / timedelta(hours=1), 
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                        ),
                    total_edotco_running_hours=ExpressionWrapper(
                            Sum(F('customer_generator_running_hours')) / timedelta(hours=1), 
                            output_field=DecimalField(max_digits=10, decimal_places=2)
                        ),
                        
                    total_hepta_calculated_fuel=Sum('internal_calculated_fuel_litre', output_field=DurationField()),
                    total_edotco_calculated_fuel=Sum('customer_calculated_fuel_litre', output_field=DurationField()),
                    total_fuel_difference=ExpressionWrapper(
                        F('total_hepta_calculated_fuel') - F('total_edotco_calculated_fuel'),
                        output_field=DecimalField(max_digits=10, decimal_places=2)
                    )
                ) \
                .order_by('region', 'zone')
            summary_data = list(summary)

        elif days:
            start_date = datetime.now() - timedelta(days=days)
            summary = eTicket.objects.filter(created_at__gte=start_date).values('region', 'zone') \
                .annotate(
                    num_tickets=Count('id'),
                    num_closed_tickets=Count('id', filter=Q(ticket_status='closed')),
                    num_valid_tickets=Count('id', filter=Q(ticket_status='TT_Valid')),
                    num_invalid_tickets=Count('id', filter=Q(ticket_status='TT_invalid')),
                    num_miss_tickets=Count('id', filter=Q(ticket_status='TT_Miss')),
                    num_running_tickets=Count('id', filter=Q(ticket_status='running')),
                    num_connected_tickets=Count('id', filter=Q(ticket_status='TT_connected')),
                    num_otw_tickets=Count('id', filter=Q(ticket_status='onTheWay')),
                    num_open_tickets=Count('id', filter=Q(ticket_status='open')),
                    num_team_assign_tickets=Count('id', filter=Q(ticket_status='team_assign')),
                    num_adhoc_PGR=Count('id', filter=Q(assigned_to__PGR_category='adhoc')),
                    num_adhoc_vehicle=Count('id', filter=Q(vehicle__vehicle_rental_type='adhoc')),                   
                    total_hepta_running_hours=ExpressionWrapper(
                    Sum(F('internal_generator_running_hours')) / timedelta(hours=1), 
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                        ),
                    total_edotco_running_hours=ExpressionWrapper(
                            Sum(F('customer_generator_running_hours')) / timedelta(hours=1), 
                            output_field=DecimalField(max_digits=10, decimal_places=2)
                        ),                   
                    total_hepta_calculated_fuel=Sum('internal_calculated_fuel_litre', output_field=DurationField()),
                    total_edotco_calculated_fuel=Sum('customer_calculated_fuel_litre', output_field=DurationField()),
                    total_fuel_difference=ExpressionWrapper(
                     F('total_edotco_calculated_fuel') -  F('total_hepta_calculated_fuel'),
                        output_field=DecimalField(max_digits=10, decimal_places=2)
                    )
                ) \
                .order_by('region', 'zone')
            summary_data = list(summary)
    form = SummaryReportForm()
    return render(request, 'tickets/edotco/summary_report.html', {
        'summary_data': summary_data,
        'form': form,
        'days': days,
        'report_date': report_date,
    })




@login_required
def summary_report_view_customerwise(request):
    form = SummaryReportForm(request.GET or {'days': 20})
    summary_data = []
    report_date = None
    days = None
    if form.is_valid():
        report_date = form.cleaned_data.get('report_date')
        days = form.cleaned_data.get('days')
        if report_date:
            summary = eTicket.objects.filter(created_at__date=report_date).values('customer_name', 'region', 'zone') \
                .annotate(
                    num_tickets=Count('id'),
                    num_closed_tickets=Count('id', filter=Q(ticket_status='closed')),
                    num_valid_tickets=Count('id', filter=Q(ticket_status='TT_Valid')),
                    num_invalid_tickets=Count('id', filter=Q(ticket_status='TT_invalid')),
                    num_miss_tickets=Count('id', filter=Q(ticket_status='TT_Miss')),
                    num_running_tickets=Count('id', filter=Q(ticket_status='running')),
                    num_connected_tickets=Count('id', filter=Q(ticket_status='TT_connected')),
                    num_otw_tickets=Count('id', filter=Q(ticket_status='onTheWay')),
                    num_open_tickets=Count('id', filter=Q(ticket_status='open')),
                    num_team_assign_tickets=Count('id', filter=Q(ticket_status='team_assign')),
                    num_adhoc_PGR=Count('id', filter=Q(assigned_to__PGR_category='adhoc')),
                    num_adhoc_vehicle=Count('id', filter=Q(vehicle__vehicle_rental_type='adhoc')),
                    total_hepta_running_hours=ExpressionWrapper(
                    Sum(F('internal_generator_running_hours')) / timedelta(hours=1), 
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                        ),
                    total_edotco_running_hours=ExpressionWrapper(
                            Sum(F('customer_generator_running_hours')) / timedelta(hours=1), 
                            output_field=DecimalField(max_digits=10, decimal_places=2)
                        ),                   
                    total_hepta_calculated_fuel=Sum('internal_calculated_fuel_litre', output_field=DurationField()),
                    total_edotco_calculated_fuel=Sum('customer_calculated_fuel_litre', output_field=DurationField()),
                    total_fuel_difference=ExpressionWrapper(
                        F('total_hepta_calculated_fuel') - F('total_edotco_calculated_fuel'),
                        output_field=DecimalField(max_digits=10, decimal_places=2)
                    )
                ) \
                .order_by('customer_name', 'region', 'zone')
            summary_data = list(summary)
        elif days:
            start_date = datetime.now() - timedelta(days=days)
            summary = eTicket.objects.filter(created_at__gte=start_date).values('customer_name', 'region', 'zone') \
                .annotate(
                    num_tickets=Count('id'),
                    num_closed_tickets=Count('id', filter=Q(ticket_status='closed')),
                    num_valid_tickets=Count('id', filter=Q(ticket_status='TT_Valid')),
                    num_invalid_tickets=Count('id', filter=Q(ticket_status='TT_invalid')),
                    num_miss_tickets=Count('id', filter=Q(ticket_status='TT_Miss')),
                    num_running_tickets=Count('id', filter=Q(ticket_status='running')),
                    num_connected_tickets=Count('id', filter=Q(ticket_status='TT_connected')),
                    num_otw_tickets=Count('id', filter=Q(ticket_status='onTheWay')),
                    num_open_tickets=Count('id', filter=Q(ticket_status='open')),
                    num_team_assign_tickets=Count('id', filter=Q(ticket_status='team_assign')),
                    num_adhoc_PGR=Count('id', filter=Q(assigned_to__PGR_category='adhoc')),
                    num_adhoc_vehicle=Count('id', filter=Q(vehicle__vehicle_rental_type='adhoc')),
                    total_hepta_running_hours=ExpressionWrapper(
                    Sum(F('internal_generator_running_hours')) / timedelta(hours=1), 
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                        ),
                    total_edotco_running_hours=ExpressionWrapper(
                            Sum(F('customer_generator_running_hours')) / timedelta(hours=1), 
                            output_field=DecimalField(max_digits=10, decimal_places=2)
                        ),                   
                    total_hepta_calculated_fuel=Sum('internal_calculated_fuel_litre', output_field=DurationField()),
                    total_edotco_calculated_fuel=Sum('customer_calculated_fuel_litre', output_field=DurationField()),
                    total_fuel_difference=ExpressionWrapper(
                        F('total_hepta_calculated_fuel') - F('total_edotco_calculated_fuel'),
                        output_field=DecimalField(max_digits=10, decimal_places=2)
                    )
                ) \
                .order_by('customer_name', 'region', 'zone')
            summary_data = list(summary)
    form = SummaryReportForm()
    return render(request, 'tickets/edotco/summary_report_customerwise.html', {
        'summary_data': summary_data,
        'form': form,
        'days': days,
        'report_date': report_date,
    })



@login_required
def summary_report_view_region(request):
    form = SummaryReportForm(request.GET or {'days': 20})
    grouped_summary_data = {}
    report_date = None
    days = None
    if form.is_valid():
        report_date = form.cleaned_data.get('report_date')
        days = form.cleaned_data.get('days')
        if report_date:          
            summary = eTicket.objects.filter(created_at__date=report_date).values('region', 'zone') \
                .annotate(
                    num_tickets=Count('id'),
                    num_closed_tickets=Count('id', filter=Q(ticket_status='closed')),
                    num_valid_tickets=Count('id', filter=Q(ticket_status='TT_Valid')),
                    num_invalid_tickets=Count('id', filter=Q(ticket_status='TT_invalid')),
                    num_miss_tickets=Count('id', filter=Q(ticket_status='TT_Miss')),
                    num_running_tickets=Count('id', filter=Q(ticket_status='running')),
                    num_connected_tickets=Count('id', filter=Q(ticket_status='TT_connected')),                    
                    num_otw_tickets=Count('id', filter=Q(ticket_status='onTheWay')),   
                    num_open_tickets=Count('id', filter=Q(ticket_status='open')), 
                    num_team_assign_tickets=Count('id', filter=Q(ticket_status='team_assign')),               
                    num_adhoc_PGR=Count('id', filter=Q(assigned_to__PGR_category='adhoc')),
                    num_adhoc_vehicle=Count('id', filter=Q(vehicle__vehicle_rental_type='adhoc')),
                    total_hepta_running_hours=ExpressionWrapper(
                    Sum(F('internal_generator_running_hours')) / timedelta(hours=1), 
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                        ),
                    total_edotco_running_hours=ExpressionWrapper(
                            Sum(F('customer_generator_running_hours')) / timedelta(hours=1), 
                            output_field=DecimalField(max_digits=10, decimal_places=2)
                        ),
                   
                   total_fuel_difference=Sum('fuel_difference', output_field=DecimalField(max_digits=10, decimal_places=2)),
                ) \
                .order_by('region', 'zone')
            for data in summary:
                region = data['region']
                if region not in grouped_summary_data:
                    grouped_summary_data[region] = []
                grouped_summary_data[region].append(data)
            form = SummaryReportForm()        
        elif days:
            start_date = datetime.now() - timedelta(days=days)
            summary = eTicket.objects.filter(created_at__gte=start_date).values('region', 'zone') \
                .annotate(
                    num_tickets=Count('id'),                   
                    num_valid_tickets=Count('id', filter=Q(ticket_status='TT_Valid')),
                    num_invalid_tickets=Count('id', filter=Q(ticket_status='TT_invalid')),
                    num_miss_tickets=Count('id', filter=Q(ticket_status='TT_Miss')),
                    num_running_tickets=Count('id', filter=Q(ticket_status='running')),
                    num_connected_tickets=Count('id', filter=Q(ticket_status='TT_connected')),                    
                    num_otw_tickets=Count('id', filter=Q(ticket_status='onTheWay')),   
                    num_open_tickets=Count('id', filter=Q(ticket_status='open')), 
                    num_team_assign_tickets=Count('id', filter=Q(ticket_status='team_assign')),                
                    num_adhoc_PGR=Count('id', filter=Q(assigned_to__PGR_category='adhoc')),
                    num_adhoc_vehicle=Count('id', filter=Q(vehicle__vehicle_rental_type='adhoc')),
                    total_hepta_running_hours=ExpressionWrapper(
                    Sum(F('internal_generator_running_hours')) / timedelta(hours=1), 
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                        ),
                    total_edotco_running_hours=ExpressionWrapper(
                            Sum(F('customer_generator_running_hours')) / timedelta(hours=1), 
                            output_field=DecimalField(max_digits=10, decimal_places=2)
                        ),                    
                    total_fuel_difference=Sum('customer_calculated_fuel_litre', output_field=DecimalField(max_digits=10, decimal_places=2)) -Sum('internal_calculated_fuel_litre', output_field=DecimalField(max_digits=10, decimal_places=2))
                ) \
                .order_by('region', 'zone')
            for data in summary:
                region = data['region']
                if region not in grouped_summary_data:
                    grouped_summary_data[region] = []
                grouped_summary_data[region].append(data)
            form = SummaryReportForm()

        else:
            pass
 
    return render(request, 'tickets/edotco/summary_report_region.html', {
        'grouped_summary_data': grouped_summary_data,
        'form': form,
        'days': days,
        'report_date': report_date,
    })


@login_required
def summary_report_view_hourly(request):
    form = SummaryReportFormHourly(request.GET or {'hours': 200})
    grouped_summary_data = {}
    hours = None
    if form.is_valid():
        hours = form.cleaned_data.get('hours')
        if hours is not None:         
            start_time = datetime.now() - timedelta(hours=hours)          
            summary = eTicket.objects.filter(created_at__gte=start_time).values('region', 'zone') \
                .annotate(
                    num_tickets=Count('id'),
                    num_closed_tickets=Count('id', filter=Q(ticket_status='closed')),
                    num_valid_tickets=Count('id', filter=Q(ticket_status='TT_Valid')),
                    num_invalid_tickets=Count('id', filter=Q(ticket_status='TT_invalid')),
                    num_miss_tickets=Count('id', filter=Q(ticket_status='TT_Miss')),
                    num_running_tickets=Count('id', filter=Q(ticket_status='running')),
                    num_connected_tickets=Count('id', filter=Q(ticket_status='TT_connected')),                    
                    num_otw_tickets=Count('id', filter=Q(ticket_status='onTheWay')),   
                    num_open_tickets=Count('id', filter=Q(ticket_status='open')), 
                    num_team_assign_tickets=Count('id', filter=Q(ticket_status='team_assign')),                 
                    num_adhoc_PGR=Count('id', filter=Q(assigned_to__PGR_category='adhoc')), 
                    num_adhoc_vehicle=Count('id', filter=Q( vehicle__vehicle_rental_type='adhoc')),
                    total_hepta_running_hours=ExpressionWrapper(
                    Sum(F('internal_generator_running_hours')) / timedelta(hours=1), 
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                        ),
                    total_edotco_running_hours=ExpressionWrapper(
                            Sum(F('customer_generator_running_hours')) / timedelta(hours=1), 
                            output_field=DecimalField(max_digits=10, decimal_places=2)
                        ),                   
                    total_fuel_difference=Sum('customer_calculated_fuel_litre', output_field=DecimalField(max_digits=10, decimal_places=2)) -Sum('internal_calculated_fuel_litre', output_field=DecimalField(max_digits=10, decimal_places=2))
                ) \
                .order_by('region', 'zone')                 
            for data in summary:
                region = data['region']
                if region not in grouped_summary_data:
                    grouped_summary_data[region] = []
                grouped_summary_data[region].append(data)                
            form = SummaryReportFormHourly()
    return render(request, 'tickets/edotco/summary_report_hourly.html', {
        'grouped_summary_data': grouped_summary_data,
        'form': form,
        'hours': hours
    })



@login_required
def zone_report_view(request):
    days = None
    start_date = None
    end_date = None  
    zone = None
    zone_tickets=[]
    form = ZoneReportForm(request.GET or {'days': 20})
    tickets = eTicket.objects.all().order_by('-created_at') 
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')   
        zone = form.cleaned_data.get('zone')   
        zone_tickets = tickets.filter(zone=zone)
        if start_date and end_date:
           zone_tickets = zone_tickets.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            zone_tickets  = zone_tickets .filter(created_at__range=(start_date, end_date))
        if zone:
            zone_tickets =zone_tickets.filter(zone=zone)
        for ticket in zone_tickets:
            internal_hours = ticket.internal_generator_running_hours.total_seconds() / 3600 if ticket.internal_generator_running_hours else 0
            customer_hours = ticket.customer_generator_running_hours.total_seconds() / 3600 if ticket.customer_generator_running_hours else 0
            fuel_difference = (internal_hours * 2.4) - (customer_hours * 2.4)
            ticket.fuel_difference = fuel_difference
    page_obj = None
    zone_tickets_per_page = 10
    paginator = Paginator(zone_tickets , zone_tickets_per_page)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    form = ZoneReportForm()
    return render(request, 'tickets/edotco/zone_report.html', {
        'zone_tickets':zone_tickets,
        'page_obj': page_obj,       
        'days': days,
        'form': form,
        'start_date': start_date,
        'end_date': end_date
    })



@login_required
def mp_report_view(request):
    days = None
    start_date = None
    end_date = None  
    mp = None
    mp_tickets=[]
    form = MPReportForm(request.GET or {'days': 20})
    tickets = eTicket.objects.all().order_by('-created_at') 
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')   
        mp = form.cleaned_data.get('mp')   
        mp_tickets = tickets.filter(mp=mp)
        if start_date and end_date:
           mp_tickets = mp_tickets.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            mp_tickets  = mp_tickets .filter(created_at__range=(start_date, end_date))
        for ticket in mp_tickets:
            internal_hours = ticket.internal_generator_running_hours.total_seconds() / 3600 if ticket.internal_generator_running_hours else 0
            customer_hours = ticket.customer_generator_running_hours.total_seconds() / 3600 if ticket.customer_generator_running_hours else 0
            fuel_difference = (internal_hours * 2.4) - (customer_hours * 2.4)
            ticket.fuel_difference = fuel_difference
        page_obj = None
        mp_tickets_per_page = 10
        paginator = Paginator(mp_tickets , mp_tickets_per_page)
        page_number = request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        query_params = request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        query_params = query_params.urlencode()
    form = MPReportForm()
    return render(request, 'tickets/edotco/mp_report.html', {
        'mp_tickets':mp_tickets,
        'page_obj': page_obj,       
        'days': days,
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
       'query_params': query_params,
    })



@login_required
def aggregated_tt_run_hour_trend_summary(request):
    form = SummaryReportChartForm(request.GET or {'days': 60}) 
    query = eTicket.objects.values('zone', 'created_at') \
        .annotate(
        trouble_tickets=Count('internal_ticket_number'),
        run_hours=Sum('internal_generator_running_hours')
    ).order_by('zone', '-created_at')   
    if form.is_valid():
        cleaned_data = form.cleaned_data        
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        days = cleaned_data.get('days')        
        if start_date and end_date:
            query = query.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            query = query.filter(created_at__range=(start_date, end_date))       
        data_list = list(query)       
        for item in data_list:
            if 'created_at' in item:
                item['created_at'] = item['created_at'].strftime('%Y-%m-%d')               
            if 'run_hours' in item:
                if item['run_hours'] is None:
                    item['run_hours'] = 0
                elif isinstance(item['run_hours'], timedelta):
                    item['run_hours'] = item['run_hours'].total_seconds() / 3600
                else:
                    item['run_hours'] = float(item['run_hours'])                  
            item['trouble_tickets'] = int(item.get('trouble_tickets', 0))           
            if item['trouble_tickets'] > 0:
                item['avg_run_hour_per_tt'] = item['run_hours'] / item['trouble_tickets']
            else:
                item['avg_run_hour_per_tt'] = 0      
        json_data = json.dumps(data_list)
        form=SummaryReportChartForm()      
        context = {
            'json_data': json_data,
            'form': form,  
            'days':days,
            'start_date':start_date,
            'end_date':end_date
        }           
        return render(request, 'tickets/edotco/tt_trend_summary.html', context)    
    else:
        context = {
            'form': form,
        }
        form=SummaryReportChartForm()       
        return render(request, 'tickets/edotco/tt_trend_summary.html', context)



@login_required
def aggregated_tt_run_hour_trend(request):
    form = SummaryReportChartForm(request.GET or {'days': 20})
    query = eTicket.objects.values('zone', 'created_at') \
        .annotate(
        trouble_tickets=Count('internal_ticket_number'),
        run_hours=Sum('internal_generator_running_hours')
    ).order_by('zone', '-created_at')
    if form.is_valid():
        cleaned_data = form.cleaned_data
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        days = cleaned_data.get('days')
        if start_date and end_date:
            query = query.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            query = query.filter(created_at__range=(start_date, end_date))
        data_list = list(query)
        for item in data_list:
            if 'created_at' in item:
                item['created_at'] = item['created_at'].strftime('%Y-%m-%d')
            if 'run_hours' in item:
                if item['run_hours'] is None:
                    item['run_hours'] = 0
                elif isinstance(item['run_hours'], timedelta):
                    item['run_hours'] = item['run_hours'].total_seconds() / 3600
                else:
                    item['run_hours'] = float(item['run_hours'])
            item['trouble_tickets'] = int(item.get('trouble_tickets', 0))
            if item['trouble_tickets'] > 0:
                item['avg_run_hour_per_tt'] = item['run_hours'] / item['trouble_tickets']
            else:
                item['avg_run_hour_per_tt'] = 0       
        json_data = json.dumps(data_list)
        cleared_form = SummaryReportChartForm()
        context = {
            'json_data': json_data,
            'form': cleared_form,
             'days':days,
            'start_date':start_date,
            'end_date':end_date
        }
        return render(request, 'tickets/edotco/tt_trend.html', context)    
    else:
        context = {
            'form': form,
        }
        return render(request, 'tickets/edotco/tt_trend.html', context)




@login_required
def individual_tt_run_hour_trend(request):
    form = SummaryReportChartForm(request.GET or {'days': 20})
    query = eTicket.objects.values('zone', 'created_at') \
        .annotate(
        trouble_tickets=Count('internal_ticket_number'),
        run_hours=Sum('internal_generator_running_hours')
    ).order_by('zone', '-created_at')
    if form.is_valid():
        cleaned_data = form.cleaned_data
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        days = cleaned_data.get('days')
        region = cleaned_data.get('region')
        zone = cleaned_data.get('zone')
        mp = cleaned_data.get('mp')
        if start_date and end_date:
            query = query.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            query = query.filter(created_at__range=(start_date, end_date))
        if region:
            query = query.filter(region=region)
        if zone:
            query = query.filter(zone=zone)
        if mp:
            query = query.filter(mp=mp)
        data_list = list(query)
        for item in data_list:
            if 'created_at' in item:
                item['created_at'] = item['created_at'].strftime('%Y-%m-%d')
            if 'run_hours' in item:
                if item['run_hours'] is None:
                    item['run_hours'] = 0
                elif isinstance(item['run_hours'], timedelta):
                    item['run_hours'] = item['run_hours'].total_seconds() / 3600
                else:
                    item['run_hours'] = float(item['run_hours'])
            item['trouble_tickets'] = int(item.get('trouble_tickets', 0))
            if item['trouble_tickets'] > 0:
                item['avg_run_hour_per_tt'] = item['run_hours'] / item['trouble_tickets']
            else:
                item['avg_run_hour_per_tt'] = 0
        json_data = json.dumps(data_list)
        cleared_form = SummaryReportChartForm()
        context = {
            'json_data': json_data,
            'form': cleared_form,
            'days': days,
            'start_date': start_date,
            'end_date': end_date
        }

        return render(request, 'tickets/edotco/tt_trend2.html', context)
    
    context = {
        'form': form,
    }
    return render(request, 'tickets/edotco/tt_trend2.html', context)



@login_required
def datewise_summary_edotco(request):
    ticket_data = eTicket.objects.values('region', 'zone', 'ticket_origin_date') \
        .annotate(
        total_tickets=Count('id'),
        total_running_hours=Sum('customer_generator_running_hours')
    ).order_by('region', 'zone', 'ticket_origin_date')
    summary_data = {}
    for item in ticket_data:
        region = item['region']
        zone = item['zone']
        date = item['ticket_origin_date']
        total_tickets = item['total_tickets']
        total_running_hours = item['total_running_hours']
        if region not in summary_data:
            summary_data[region] = {}
        if date not in summary_data[region]:
            summary_data[region][date] = {}
        summary_data[region][date][zone] = {
            'total_tickets': total_tickets,
            'total_running_hours': total_running_hours,
        }
    return render(request, 'tickets/edotco/date_wise_summary_edotco.html', {'summary_data': summary_data})


def tt_management(request):
    return render(request, 'tickets/tt_management.html')




####################### API setting/views ##################################################

@api_view(['GET', 'POST'])
def eTickets_details_api2(request):
    if request.method == 'GET':
        tickets = eTicket.objects.all()
        serializer = eTicketSerializer(tickets, many=True)
        return Response( serializer.data)
    elif request.method == 'POST':
        serializer = eTicketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def eTickets_details_api(request):
    if request.method == 'GET':
        tickets = eTicket.objects.all()
        serializer = eTicketSerializer(tickets, many=True)
        return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
def eTicket_update_api(request, id):
    try:
        ticket = eTicket.objects.get(pk=id)
        if request.method == 'GET':
            serializer = eTicketSerializer(ticket)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = eTicketSerializer(ticket, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            ticket.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    except eTicket.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
def create_child_ticket_api(request, parent_ticket_id):
    parent_ticket_id = request.data.get('parent_ticket_id')
    child_internal_generator_start_time_str = request.data.get('start_time')
    child_internal_generator_stop_time_str = request.data.get('end_time')
    child_tt_image = request.data.get('child_tt_image')
    file_path = None
    try:
        child_internal_generator_start_time = datetime.strptime(child_internal_generator_start_time_str, '%H:%M %p').time()
        child_internal_generator_stop_time = datetime.strptime(child_internal_generator_stop_time_str, '%H:%M %p').time()
        if child_tt_image:
            unique_filename = str(uuid.uuid4()) 
            file_name = 'child_tt_image/' + unique_filename
            file_path = default_storage.save(file_name, ContentFile(base64.b64decode(child_tt_image)))
    except ValueError:
        return Response({'error': 'Invalid time format'}, status=status.HTTP_400_BAD_REQUEST)
    parent_ticket = get_object_or_404(eTicket, id=parent_ticket_id)
    if request.method == 'POST':
        child_ticket = ChildTicket(
            parent_ticket=parent_ticket,
            child_internal_generator_start_time=child_internal_generator_start_time,
            child_internal_generator_stop_time=child_internal_generator_stop_time,
            child_ticket_number=generate_unique_ticket_number(),
            child_tt_image = file_path
        )
        child_ticket.save()
        return Response({'message': 'Child ticket created successfully'}, status=status.HTTP_201_CREATED)
    return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)




def format_duration_to_hms(duration):
    total_seconds = duration.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"





def datewise_summary_edotco(request):
    form = SummaryReportChartForm(request.GET or {'days': 60})
    tickets = eTicket.objects.all()
    if form.is_valid():
        cleaned_data = form.cleaned_data
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        days = cleaned_data.get('days')
        region = cleaned_data.get('region')
        zone = cleaned_data.get('zone')

        if start_date and end_date:
            tickets = tickets.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            tickets = tickets.filter(created_at__range=(start_date, end_date))
        if region:
            tickets = tickets.filter(region=region)
        if zone:
            tickets = tickets.filter(zone=zone)

  

    rangpur_zones = ['Rangpur', 'Dinajpur', 'Rajshahi', 'Bagura']
    sylhet_zones = ['Sylhet', 'Moulovibazar', 'Mymensingh', 'Kisorganj', 'Tangail']

    report_summary = (
        tickets.values('ticket_origin_date', 'zone')
        .annotate(
            TT=Count('internal_ticket_number'),
            PGRH=Sum('internal_generator_running_hours')
        )
    )
    
    # Preparing the data structure
    aggregated_data = {}
    rajshahi_tt = 0
    rajshahi_pgrh = 0
    rangpur_tt = 0
    rangpur_pgrh = 0
    dinajpur_tt = 0
    dinajpur_pgrh = 0
    bagura_tt = 0
    bagura_pgrh = 0

    sylhet_tt = 0
    sylhet_pgrh = 0
    moulovibazar_tt = 0
    moulovibazar_pgrh = 0

    mymensingh_tt = 0
    mymensingh_pgrh = 0
    kisorganj_tt = 0
    kisorganj_pgrh = 0
    tangail_tt =0
    tangail_pgrh = 0

    rangpur_region_tt = 0
    rangpur_region_pgrh = 0
    sylhet_region_tt = 0
    sylhet_region_pgrh = 0

    grand_total_tt = 0
    grand_total_pgrh = 0

    
    
    for entry in report_summary:
        date = entry['ticket_origin_date']
        zone = entry['zone']
        tt = entry['TT']
        pgrh = entry['PGRH'].total_seconds() / 3600 if entry['PGRH'] else 0  # Convert to hours

        if date not in aggregated_data:
            aggregated_data[date] = {}

        aggregated_data[date][zone] = {'TT': tt, 'PGRH': pgrh}

        # Calculate subtotals
        if zone == 'Rajshahi':
            rajshahi_tt += tt
            rajshahi_pgrh += pgrh
        elif zone == 'Rangpur':
            rangpur_tt += tt
            rangpur_pgrh += pgrh

        elif zone == 'Dinajpur':
            dinajpur_tt += tt
            dinajpur_pgrh += pgrh

        elif zone == 'Bagura':
            bagura_tt += tt
            bagura_pgrh += pgrh

        elif zone == 'Sylhet':
            sylhet_tt += tt
            sylhet_pgrh += pgrh

        elif zone == 'Moulovibazar':
            moulovibazar_tt += tt
            moulovibazar_pgrh += pgrh

        elif zone == 'Mymensingh':
            mymensingh_tt += tt
            mymensingh_pgrh += pgrh

        elif zone == 'Kisorganj':
            kisorganj_tt += tt
            kisorganj_pgrh += pgrh

        elif zone == 'Tangail':
            tangail_tt += tt
            tangail_pgrh += pgrh

        # Aggregate for region
        if zone in rangpur_zones:
            rangpur_region_tt += tt
            rangpur_region_pgrh += pgrh
       
        elif zone in sylhet_zones:
            sylhet_region_tt += tt
            sylhet_region_pgrh += pgrh
        
        grand_total_tt += tt
        grand_total_pgrh += pgrh

    form = SummaryReportChartForm()
    context = {
        'report_summary': aggregated_data,
        'rajshahi_tt': rajshahi_tt,
        'rajshahi_pgrh': rajshahi_pgrh,
        'rangpur_tt': rangpur_tt,
        'rangpur_pgrh': rangpur_pgrh,
        'dinajpur_tt': dinajpur_tt,
        'dinajpur_pgrh': dinajpur_pgrh,
        'bagura_tt': bagura_tt,
        'bagura_pgrh': bagura_pgrh,

        'sylhet_tt': sylhet_tt,
        'sylhet_pgrh': sylhet_pgrh,
        'moulovibazar_tt': moulovibazar_tt,
        'moulovibazar_pgrh': moulovibazar_pgrh,

        'mymensingh_tt': mymensingh_tt,
        'mymensingh_pgrh': mymensingh_pgrh,
        'kissorganj_tt': kisorganj_tt,
        'kisorganj_pgrh': kisorganj_pgrh,
        'tangail_tt':tangail_tt,
        'tangail_pgrh':tangail_pgrh,

        'rangpur_region_tt': rangpur_region_tt,
        'rangpur_region_pgrh': rangpur_region_pgrh,
        'sylhet_region_tt': sylhet_region_tt,
        'sylhet_region_pgrh': sylhet_region_pgrh,

        'grand_total_tt':grand_total_tt,
        'grand_total_pgrh':grand_total_pgrh,
        'form':form
       
    }
    
 

    return render(request, 'tickets\edotco\date_wise_summary_edotco2.html', context)
