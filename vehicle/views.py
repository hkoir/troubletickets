import xlsxwriter
import random
import csv
from itertools import groupby
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,JsonResponse

from django.shortcuts import render, redirect,get_object_or_404
from django.db.models import Sum, Avg,Count,Q,Case, When, IntegerField,F,Max,DurationField, DecimalField,FloatField,ExpressionWrapper,Value
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal
from .forms import AdVehicleForm, AddVehicleExpensesForm
from .forms import VehicleDetailsForm,VehicleDatabaseViewForm
from .forms import VehicleFaulttForm,VehiclePaymentForm,RentalPeriodForm
from.forms import vehicleSummaryReportForm,FuelRefillForm,UpdateVehicleDatabaeForm
from .models import VehicleRuniningData, AddVehicleInfo, FuelRefill,VehicleRentalCost,Vehiclefault
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from tickets.forms import SummaryReportChartForm
from tickets.models import eTicket
from tickets .views import generate_unique_finance_requisition_number
import calendar
from dailyexpense.models import DailyExpenseRequisition

from django.core.exceptions import ValidationError

from.forms import AdhocAttendanceIntimeForm,AdhocAttendanceUpdateOuttimeForm,AdhocPaymentForm,AdhocRequisitionForm,AdhocRequisitionStatusForm,vehicleSummaryReportForm
from.models import AdhocVehicleRequisition,AdhocVehicleAttendance,AdhocVehiclePayment
from django.db.models.functions import Coalesce, Round
from django.conf import settings
from decimal import Decimal
from .forms import AdhocVehiclePaymentFormCommon


@login_required
def create_vehicle(request):
    if request.method == 'POST':   
        form = AdVehicleForm(request.POST, request.FILES)
        if form.is_valid():        
            form.instance.vehicle_add_requester = request.user
            form.instance.vehicle_id = generate_unique_finance_requisition_number()
            form.save()
            return redirect('vehicle:view_vehicle_info')
    else:     
        form = AdVehicleForm()
    return render(request, 'vehicle/create_vehicle.html', {'form': form})



@login_required
def view_vehicle_info(request): 
    region = None
    zone = None
    mp = None
    vehicle_reg_number = None

    form = VehicleDatabaseViewForm(request.GET)

    vehicle_info = AddVehicleInfo.objects.all().order_by('-created_at')

    if form.is_valid():      
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        vehicle_reg_number = form.cleaned_data.get('vehicle_reg_number')

        if region:
             vehicle_info =  vehicle_info.filter(region=region)
        if zone:
             vehicle_info =  vehicle_info.filter(zone=zone)
        if mp:
            vehicle_info =  vehicle_info.filter(mp=mp)

        if vehicle_reg_number:
              vehicle_info =  vehicle_info.filter(vehicle_reg_number=vehicle_reg_number)

    # Pagination logic
    page_obj = None
    vehicle_per_page = 10
    paginator = Paginator(vehicle_info, vehicle_per_page)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    form = VehicleDatabaseViewForm()
    return render(request, 'vehicle/view_vehicle_info.html', {
        'vehicle_info': vehicle_info,
        'page_obj': page_obj,
        'form': form,       
        'region': region,
        'zone': zone,
        'mp': mp,
    })



@login_required
def zonewise_vehicle(request):
    total_vehicle = AddVehicleInfo.objects.aggregate(total_vehicle=Count("id"))
    total_permanent_vehicle = AddVehicleInfo.objects.aggregate(total_permanent_vehicle=Count("id",filter=Q(vehicle_rental_type='permanent')))
    total_adhoc_vehicle = AddVehicleInfo.objects.aggregate(total_adhoc_vehicle=Count("id",filter=Q(vehicle_rental_type='adhoc')))
   
    total_vehicle_count = total_vehicle['total_vehicle']
    total_permanent_vehicle_count = total_permanent_vehicle['total_permanent_vehicle']
    total_adhoc_vehicle_count = total_adhoc_vehicle['total_adhoc_vehicle']
  

    zonewise_vehicle = AddVehicleInfo.objects.values('region', 'zone').annotate(
        total_count=Count('id'),  
        total_permanent_vehicle_count = Count('id',filter=Q(vehicle_rental_type='permanent')), 
        total_adhoc_vehicle_count = Count('id',filter=Q(vehicle_rental_type='adhoc'))     
    )
    
    zonewise_data = []
    for entry in zonewise_vehicle:
        region = entry['region']
        zone = entry['zone']

        zonewise_data.append({
            'region': region,
            'zone': zone,
            'total_count': entry['total_count'],
            'total_permanent_vehicle_count': entry['total_permanent_vehicle_count'],
            'total_adhoc_vehicle_count': entry['total_adhoc_vehicle_count'],
             })
     
    report = AddVehicleInfo.objects.values('vehicle_owner_company_name', 'region', 'zone', 'mp').annotate(
        total_count=Count('id'),
        total_permanent_vehicle_count = Count('id',filter=Q(vehicle_rental_type='permanent')), 
        total_adhoc_vehicle_count = Count('id',filter=Q(vehicle_rental_type='adhoc'))   

    )

    report_data = {}
    for entry in report:
        supplier = entry['vehicle_owner_company_name']       
        if supplier not in report_data:
            report_data[supplier] = {
                'entries': [],      
                'total_count': 0,
                'total_permanent_vehicle_count':0,
                'total_adhoc_vehicle_count':0


            }
        report_data[supplier]['entries'].append(entry)   
        report_data[supplier]['total_count'] += entry['total_count']
        report_data[supplier]['total_permanent_vehicle_count'] += entry['total_permanent_vehicle_count']
        report_data[supplier]['total_adhoc_vehicle_count'] += entry['total_adhoc_vehicle_count']

    return render(request, 'vehicle/zone_wise_vehicle.html', 
                  {'report_data': report_data,
                   'total_vehicle_count':total_vehicle_count, 
                   'total_permanent_vehicle_count':total_permanent_vehicle_count,
                    'total_adhoc_vehicle_count':total_adhoc_vehicle_count,              
                    'zonewise_data': zonewise_data,
                     })


@login_required
def update_vehicle_database(request, vehicle_id):
    vehicle_info= AddVehicleInfo.objects.get(id=vehicle_id)
    if request.user.is_authenticated:
        user_role = request.user.manager_level
    else:
         return redirect('account:login')

    if request.method == 'POST': 
        form = UpdateVehicleDatabaeForm(request.POST,request.FILES, instance=vehicle_info,user_role=user_role)
        if form.is_valid():
            form.save()
            return redirect('vehicle:view_vehicle_info') 
    else:
        initial_data = {'vehicle_owner_address': vehicle_info.vehicle_owner_address}     
        form = UpdateVehicleDatabaeForm(instance=vehicle_info, initial=initial_data, user_role=user_role)
        print("Vehicle Owner Address:", vehicle_info.vehicle_owner_address)

    return render(request, 'vehicle/update_vehicle.html', {'form': form,'vehicle_info':vehicle_info,'vehicle_owner_address': vehicle_info.vehicle_owner_address})



@login_required
def delete_vehicle_database(request, vehicle_id):
    vehicle_info = get_object_or_404(AddVehicleInfo, id=vehicle_id)

    if request.method == 'POST':
        if request.POST.get('confirm') == 'yes': 
            vehicle_info.delete()
            messages.success(request, 'Vehicle deleted successfully.')
            return redirect('vehicle:view_vehicle_info')  
        else:
            return redirect('vehicle:view_vehicle_info')

    return render(request,'vehicle/delete_record.html', {' vehicle_info': vehicle_info})



@login_required
def create_vehicle_expenses(request):
    if request.method == 'POST':
        form = AddVehicleExpensesForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.vehicle_expense_add_requester = request.user
            form.instance.vehicle_expense_id = generate_unique_finance_requisition_number()
            form.save()
            return redirect('vehicle:view_vehicle_travel_data')
        else:
            print("Form is invalid:", form.errors)
            print("Submitted data:", request.POST)
            for field in form:
                print(f"Field: {field.name}, Errors: {field.errors}, Value: {field.value()}")
    else:
        form = AddVehicleExpensesForm()

    return render(request, 'vehicle/create_vehicle_expenses.html', {'form': form})


@login_required
def view_vehicle_travel_data(request): 
    vehicle_number=None   
    form = vehicleSummaryReportForm(request.GET or None)
    vehicle_expenses = VehicleRuniningData.objects.all().order_by('-created_at')
    if form.is_valid():      
        vehicle_number = form.cleaned_data.get('vehicle_number')
    if vehicle_number:
        vehicle_expenses =vehicle_expenses.filter(vehicle__vehicle_reg_number=vehicle_number)    

    paginator = Paginator(vehicle_expenses, 10) 
    page_number = request.GET.get('page')

    try:
        vehicle_expenses = paginator.page(page_number)
    except PageNotAnInteger:
        vehicle_expenses = paginator.page(1)
    except EmptyPage:
        vehicle_expenses = paginator.page(paginator.num_pages)

    form=vehicleSummaryReportForm()
    return render(request, 'vehicle/view_vehicle_travel_data.html', {'vehicle_expenses': vehicle_expenses,'form':form})




@login_required
def create_fuel_refill(request):
    if request.method == 'POST':   
        form = FuelRefillForm(request.POST, request.FILES)
        if form.is_valid():        
            form.instance.refill_requester = request.user
            form.instance.fuel_refill_code = generate_unique_finance_requisition_number()
            form.save()
            return redirect('vehicle:view_fuel_refill')
    else:     
        form = FuelRefillForm()
    return render(request, 'vehicle/fuel_refill_form.html', {'form': form})



@login_required
def view_fuel_refill(request): 
    vehicle_number=None   
    form = vehicleSummaryReportForm(request.GET or None)
    fuel_refill = FuelRefill.objects.all().order_by('-created_at')
    if form.is_valid():      
        vehicle_number = form.cleaned_data.get('vehicle_number')
    if vehicle_number:
         fuel_refill = fuel_refill.filter(vehicle__vehicle_reg_number=vehicle_number) 

    if 'download_csv' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="expense_approval_status.csv"'
        writer = csv.writer(response)
        writer.writerow(['created_at','Requester'])

        for expense_requisition in fuel_refill:
            writer.writerow([
                expense_requisition.created_at,
                expense_requisition.refill_requester,               
            ])

        return response

    paginator = Paginator( fuel_refill, 10) 
    page_number = request.GET.get('page')

    try:
        fuel_refill = paginator.page(page_number)
    except PageNotAnInteger:
        fuel_refill = paginator.page(1)
    except EmptyPage:
        fuel_refill = paginator.page(paginator.num_pages)

    form = vehicleSummaryReportForm()
    return render(request, 'vehicle/view_fuel_refill.html', {'fuel_refill':fuel_refill,'form':form})




@login_required
def create_vehicle_payment(request):
    if request.method == 'POST':   
        form = VehiclePaymentForm(request.POST, request.FILES)
        if form.is_valid():       
            form.instance.vehicle_rent_paid_id = generate_unique_finance_requisition_number()
            form.save()
            return redirect('vehicle:view_vehicle_payment')
    else:     
        form =VehiclePaymentForm()
    return render(request, 'vehicle/create_vehicle_payment.html', {'form': form})




@login_required
def view_vehicle_payment(request):
    vehicle_payment_data = VehicleRentalCost.objects.all().order_by('-created_at')  
    vehicle_number=None   
    form = vehicleSummaryReportForm(request.GET or None)  
    if form.is_valid():      
        vehicle_number = form.cleaned_data.get('vehicle_number')
    if vehicle_number:
        vehicle_payment_data=vehicle_payment_data.filter(vehicle__vehicle_reg_number=vehicle_number)  
    form = vehicleSummaryReportForm()  
    return render(request, 'vehicle/view_vehicle_payment.html', {'vehicle_payment_data': vehicle_payment_data,'form':form})



@login_required
def create_vehicle_fault(request):
    if request.method == 'POST':   
        form = VehicleFaulttForm(request.POST, request.FILES)
        if form.is_valid():       
            form.instance.vehicle_rent_paid_id = generate_unique_finance_requisition_number()
            form.save()
            return redirect('vehicle:view_vehicle_fault')
    else:     
        form =VehicleFaulttForm()
    return render(request, 'vehicle/create_vehicle_fault.html', {'form': form})



@login_required
def update_vehicle_fault(request,vehicle_id):
    vehicle_info= Vehiclefault.objects.get(id=vehicle_id)

    if request.method == 'POST': 
        form = VehicleFaulttForm(request.POST,request.FILES, instance=vehicle_info)
        if form.is_valid():
            form.save()
            return redirect('vehicle:view_vehicle_fault') 
    else:
          
        form = VehicleFaulttForm(instance=vehicle_info)   
    return render(request, 'vehicle/create_vehicle_fault.html', {'form': form})




@login_required
def view_vehicle_fault(request):
    vehiclefault = Vehiclefault.objects.all()   
    vehicle_number=None   
    form = vehicleSummaryReportForm(request.GET or None)  
    if form.is_valid():      
        vehicle_number = form.cleaned_data.get('vehicle_number')
    if vehicle_number:
        vehiclefault=vehiclefault.filter(vehicle__vehicle_reg_number=vehicle_number)  
    form = vehicleSummaryReportForm() 
    return render(request, 'vehicle/view_vehicle_fault.html', {'vehiclefault': vehiclefault,'form':form})



@login_required
def vehicle_summary_report(request):
    form = vehicleSummaryReportForm(request.GET or {'days': 20})
    vehicle_running_data = VehicleRuniningData.objects.all().order_by('-created_at')
    total_refill_amount_qs = FuelRefill.objects.all()  # Renamed to avoid conflict
    vehicle_completed_tickets_count_qs = eTicket.objects.all()  # Renamed to avoid conflict
    vehicle_completed_pg_runhour_count_qs = eTicket.objects.all()

    vehicle_summary_reports = {}
    processed_vehicles = {}
    days = None
    start_date = None
    end_date = None
    vehicle = []
    total_fuel_cost = 0
   

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')

        if start_date and end_date:
            vehicle_running_data = vehicle_running_data.filter(created_at__range=(start_date, end_date))
            total_refill_amount_qs = total_refill_amount_qs.filter(created_at__range=(start_date, end_date))
            vehicle_completed_tickets_count_qs = vehicle_completed_tickets_count_qs.filter(created_at__range=(start_date, end_date))
           

        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
           
            vehicle_running_data = vehicle_running_data.filter(created_at__range=(start_date, end_date))
            total_refill_amount_qs = total_refill_amount_qs.filter(created_at__range=(start_date, end_date))
            vehicle_completed_tickets_count_qs = vehicle_completed_tickets_count_qs.filter(created_at__range=(start_date, end_date))
           

        if region:
            vehicle_running_data = vehicle_running_data.filter(region=region)
            total_refill_amount_qs = total_refill_amount_qs.filter(region=region)
            vehicle_completed_tickets_count_qs = vehicle_completed_tickets_count_qs.filter(region=region)
            vehicle_completed_pg_runhour_count_qs = vehicle_completed_pg_runhour_count_qs.filter(region=region)
        if zone:
            vehicle_running_data = vehicle_running_data.filter(zone=zone)
            total_refill_amount_qs = total_refill_amount_qs.filter(zone=zone)
            vehicle_completed_tickets_count_qs = vehicle_completed_tickets_count_qs.filter(zone=zone)
            
        if mp:
            vehicle_running_data = vehicle_running_data.filter(mp=mp)
            total_refill_amount_qs = total_refill_amount_qs.filter(mp=mp)
            vehicle_completed_tickets_count_qs = vehicle_completed_tickets_count_qs.filter(mp=mp)
            

    for data in vehicle_running_data:
        region = data.region
        zone = data.zone
        mp = data.mp
        vehicle = data.vehicle

        if vehicle in processed_vehicles:
            continue

        processed_vehicles[vehicle] = data

        if region not in vehicle_summary_reports:
            vehicle_summary_reports[region] = {}
        if zone not in vehicle_summary_reports[region]:
            vehicle_summary_reports[region][zone] = {}
        if vehicle not in vehicle_summary_reports[region][zone]:
            vehicle_summary_reports[region][zone][vehicle] = {
                'total_refill_amount': 0,
                'total_kilometer_run': 0,
                'total_fuel_consumed': 0,
                'total_kilometer_run_from_refill_data':0,
                'total_kilometer_run_from_running_data':0,
                'total_kilometer_cost_from_refill': 0,
                'total_kilometer_cost_from_run': 0,
            }

        total_refill_amount = total_refill_amount_qs.filter(vehicle__vehicle_reg_number=data.vehicle.vehicle_reg_number).aggregate(total_refill_amount=Sum('refill_amount'))['total_refill_amount'] or 0
        total_kilometer_run_from_refill_data = total_refill_amount_qs.filter(vehicle__vehicle_reg_number=data.vehicle.vehicle_reg_number).aggregate( total_kilometer_run_from_refill_data=Sum('vehicle_kilometer_run'))['total_kilometer_run_from_refill_data'] or 0

        if total_kilometer_run_from_refill_data <= 150:
            total_kilometer_cost_from_refill = total_kilometer_run_from_refill_data * 9.0
        else:
            total_kilometer_cost_from_refill = 150 *9.0 + (total_kilometer_run_from_refill_data -150) * 16.0


        total_kilometer_run_from_running_data = vehicle_running_data.filter(region=region, zone=zone, vehicle=data.vehicle).aggregate(total_kilometer_run_from_running_data =Sum('total_kilometer_run'))['total_kilometer_run_from_running_data'] or 0
        if  total_kilometer_run_from_running_data <= 150:
            total_kilometer_cost_from_run =  total_kilometer_run_from_running_data * 9.0
        else:
            total_kilometer_cost_from_run = Decimal(150.0) * Decimal(9.0) + (total_kilometer_run_from_running_data -150) * Decimal(16.0)

        
        total_fuel_consumed = vehicle_running_data.filter(region=region, zone=zone, vehicle=data.vehicle).aggregate(total_fuel_consumed=Sum('total_fuel_consumed'))['total_fuel_consumed'] or 0

        net_fuel_balance = total_refill_amount - total_fuel_consumed

        vehicle_completed_tickets_count = vehicle_completed_tickets_count_qs.filter(vehicle__vehicle_reg_number=data.vehicle.vehicle_reg_number).count()
        vehicle_completed_pg_runhour_count =vehicle_completed_tickets_count_qs.filter(vehicle__vehicle_reg_number=data.vehicle.vehicle_reg_number).aggregate(total_runhour=Sum('internal_generator_running_hours'))['total_runhour'] or 0

        vehicle_fuel_unit_price = data.vehicle.vehicle_fuel_unit_price
        if total_fuel_consumed and vehicle_fuel_unit_price != 0:
            total_fuel_cost = Decimal(total_fuel_consumed) * Decimal(vehicle_fuel_unit_price)

        if vehicle_completed_tickets_count != 0:
            cost_per_tt = total_fuel_cost / vehicle_completed_tickets_count
        else:
            cost_per_tt = 0

        vehicle_summary_reports[region][zone][vehicle]['total_refill_amount'] += total_refill_amount
        vehicle_summary_reports[region][zone][vehicle]['total_kilometer_run_from_refill_data'] += total_kilometer_run_from_refill_data
        vehicle_summary_reports[region][zone][vehicle]['total_kilometer_run_from_running_data'] += total_kilometer_run_from_running_data 
        vehicle_summary_reports[region][zone][vehicle]['total_fuel_consumed'] += total_fuel_consumed
        vehicle_summary_reports[region][zone][vehicle]['net_fuel_balance'] = net_fuel_balance
        vehicle_summary_reports[region][zone][vehicle]['vehicle_completed_tickets_count'] = vehicle_completed_tickets_count
        vehicle_summary_reports[region][zone][vehicle]['vehicle_completed_pg_runhour_count'] = vehicle_completed_pg_runhour_count
        vehicle_summary_reports[region][zone][vehicle]['cost_per_tt'] = cost_per_tt

        vehicle_summary_reports[region][zone][vehicle]['total_kilometer_cost_from_refill'] = total_kilometer_cost_from_refill
        vehicle_summary_reports[region][zone][vehicle]['total_kilometer_cost_from_run'] = total_kilometer_cost_from_run


    paginator = Paginator(vehicle_running_data, 10)  # 10 items per page
    page_number = request.GET.get('page')
    try:
        vehicle_running_data = paginator.page(page_number)
    except PageNotAnInteger:
        vehicle_running_data = paginator.page(1)
    except EmptyPage:
        vehicle_running_data = paginator.page(paginator.num_pages)

    form = vehicleSummaryReportForm()
    return render(request, 'vehicle/vehicle_summary_report.html', 
        {'vehicle_summary_reports': vehicle_summary_reports,
        'vehicle_running_data': vehicle_running_data,
         'form':form,
         'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'region': region,
        'zone': zone,
        'mp': mp,
        'vehicle':vehicle
         })



@login_required
def management_summary_report(request):
    form = vehicleSummaryReportForm(request.GET or {'days': 20})
    vehicle_data = VehicleRuniningData.objects.all()
    fuel_refill_data = FuelRefill.objects.all()
    ticket_data = eTicket.objects.all()
    vehicle_fuel_cash_advance = DailyExpenseRequisition.objects.all()

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')

        if start_date and end_date:
            vehicle_data = vehicle_data.filter(created_at__range=(start_date, end_date))
            fuel_refill_data = fuel_refill_data.filter(created_at__range=(start_date, end_date))
            ticket_data = ticket_data.filter(created_at__range=(start_date, end_date))
            vehicle_fuel_cash_advance = vehicle_fuel_cash_advance.filter(created_at__range=(start_date, end_date))

        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            vehicle_data = vehicle_data.filter(created_at__range=(start_date, end_date))
            fuel_refill_data = fuel_refill_data.filter(created_at__range=(start_date, end_date))
            ticket_data = ticket_data.filter(created_at__range=(start_date, end_date))
            vehicle_fuel_cash_advance = vehicle_fuel_cash_advance.filter(created_at__range=(start_date, end_date))

        if region:
            vehicle_data = vehicle_data.filter(region=region)
            fuel_refill_data = fuel_refill_data.filter(region=region)
            ticket_data = ticket_data.filter(region=region)
            vehicle_fuel_cash_advance = vehicle_fuel_cash_advance.filter(region=region)
        if zone:
            vehicle_data = vehicle_data.filter(zone=zone)
            fuel_refill_data = fuel_refill_data.filter(zone=zone)
            ticket_data = ticket_data.filter(zone=zone)
            vehicle_fuel_cash_advance = vehicle_fuel_cash_advance.filter(zone=zone)
        if mp:
            vehicle_data = vehicle_data.filter(mp=mp)
            fuel_refill_data = fuel_refill_data.filter(mp=mp)
            ticket_data = ticket_data.filter(mp=mp)
            vehicle_fuel_cash_advance = vehicle_fuel_cash_advance.filter(mp=mp)

    vehicle_data = vehicle_data.values('region', 'zone').annotate(
        total_fuel_consumed=Sum('total_fuel_consumed'),
        total_kilometer_run=Sum('total_kilometer_run')
    )
    fuel_refill_data = fuel_refill_data.values('region', 'zone').annotate(
        total_refill_amount=Sum('refill_amount'),
        total_fuel_consumed_refill=Sum('vehicle_fuel_consumed')
    )
    ticket_data = ticket_data.values('region', 'zone').annotate(
        total_ticket=Count('internal_ticket_number')
    )

    vehicle_fuel_cash_advance = vehicle_fuel_cash_advance.values('region', 'zone').annotate(
        total_requisition_amount=Sum('requisition_amount', filter=Q(purpose='vehicle_local_fuel_purchase'))
    )

    # Convert querysets to dictionaries for easier matching
    vehicle_dict = { (v['region'], v['zone']): v for v in vehicle_data }
    fuel_dict = { (f['region'], f['zone']): f for f in fuel_refill_data }
    ticket_dict = { (t['region'], t['zone']): t for t in ticket_data }
    vehicle_fuel_cash_advance_dict = { (c['region'], c['zone']): c for c in vehicle_fuel_cash_advance }

    combined_data = []

    all_regions_zones = set(vehicle_dict.keys()).union(fuel_dict.keys()).union(ticket_dict.keys()).union(vehicle_fuel_cash_advance_dict.keys())

    for region_zone in all_regions_zones:
        region, zone = region_zone
        vehicle_item = vehicle_dict.get(region_zone, {'total_fuel_consumed': 0, 'total_kilometer_run': 0})
        fuel_item = fuel_dict.get(region_zone, {'total_refill_amount': 0, 'total_fuel_consumed_refill': 0})
        ticket_item = ticket_dict.get(region_zone, {'total_ticket': 0})
        vehicle_fuel_cash_advance_item = vehicle_fuel_cash_advance_dict.get(region_zone, {'total_requisition_amount': 0})

        fuel_consumed_per_ticket = 0
        if ticket_item['total_ticket'] != 0:
            fuel_consumed_per_ticket = vehicle_item['total_fuel_consumed'] / ticket_item['total_ticket']
        kilometer_run_per_litre = 0
        if vehicle_item['total_fuel_consumed'] != 0:
            kilometer_run_per_litre = vehicle_item['total_kilometer_run'] / vehicle_item['total_fuel_consumed']

        combined_data.append({
            'region': region,
            'zone': zone,
            'total_refill_amount': fuel_item['total_refill_amount'],
            'total_fuel_consumed_refill': fuel_item['total_fuel_consumed_refill'],
            'total_fuel_consumed': vehicle_item['total_fuel_consumed'],
            'total_kilometer_run': vehicle_item['total_kilometer_run'],
            'total_ticket': ticket_item['total_ticket'],
            'fuel_consumed_per_ticket': fuel_consumed_per_ticket,
            'kilometer_run_per_litre': kilometer_run_per_litre,
            'total_requisition_amount': vehicle_fuel_cash_advance_item['total_requisition_amount']
        })

    form = vehicleSummaryReportForm()
    return render(request, 'vehicle/management_report.html', 
                  {
                      'combined_data': combined_data,
                      'form': form,
                      'start_date': start_date,
                      'end_date': end_date,
                      'days': days
                  })


## this is also vehicle cost performance #####################
def vehicle_overtime_calc(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None
    vehicle_rent_per_day = None


    form = SummaryReportChartForm(request.GET or {'days': 20})  
    running_data_queryset = VehicleRuniningData.objects.all().order_by('-created_at')
    
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')

        if start_date and end_date:
            running_data_queryset =  running_data_queryset.filter(created_at__range=(start_date, end_date))
            days = (end_date - start_date).days + 1
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            running_data_queryset = running_data_queryset.filter(created_at__range=(start_date, end_date))
          
        if region:
             running_data_queryset =  running_data_queryset.filter(region=region)
        if zone:
             running_data_queryset =  running_data_queryset.filter(zone=zone)
        if mp:
             running_data_queryset =  running_data_queryset.filter(mp=mp)
   
    datewise_running_data = {}
    vehicle_overtime_totals = {}
    friday_saturday = None


    for data in running_data_queryset:    
        date = data.start_time
        friday_saturday = date.weekday() in [4, 5]
        vehicle_reg_number = data.vehicle.vehicle_reg_number
        vehicle_rental_category = data.vehicle.vehicle_rental_category
        running_hours = data.running_hours
        running_hours = running_hours or 0
        overtime_rate = data.vehicle.vehicle_driver_overtime_rate
        if data.vehicle.vehicle_rental_category == 'daily' and data.vehicle.vehicle_rent is not None:
            if date:
                vehicle_rent_per_day = data.vehicle.vehicle_rent
        elif data.vehicle.vehicle_rental_category == 'monthly' and data.vehicle.vehicle_rent is not None:
            vehicle_rent_per_day = data.vehicle.vehicle_rent / 30
        else:
            vehicle_rent_per_day = 0  

        if vehicle_reg_number not in datewise_running_data:
            datewise_running_data[vehicle_reg_number] = {}

        if date not in datewise_running_data[vehicle_reg_number]:
            datewise_running_data[vehicle_reg_number][date] = {'total_running_hours': 0, 'overtime_running_hours': 0}

        datewise_running_data[vehicle_reg_number][date]['total_running_hours'] += running_hours

      
        if friday_saturday: 
            overtime_running_hours = running_hours
            remarks = 'Weekened'
           
        else:
            overtime_running_hours = max(0, datewise_running_data[vehicle_reg_number][date]['total_running_hours'] - 8) 
            remarks = 'Weekday'
        datewise_running_data[vehicle_reg_number][date]['overtime_running_hours'] = overtime_running_hours
                       
        overtime_cost = float(overtime_rate) * overtime_running_hours 
         
       
        datewise_running_data[vehicle_reg_number][date]['overtime_cost'] = overtime_cost
        datewise_running_data[vehicle_reg_number][date]['overtime_rate'] = overtime_rate
        datewise_running_data[vehicle_reg_number][date]['vehicle_reg_number'] = vehicle_reg_number
        datewise_running_data[vehicle_reg_number][date]['vehicle_rent_per_day'] = vehicle_rent_per_day
        datewise_running_data[vehicle_reg_number][date]['vehicle_rental_category'] = vehicle_rental_category
        datewise_running_data[vehicle_reg_number][date]['remarks'] = remarks 

    datewise_running_data_list = [(vehicle_reg_number, data) for vehicle_reg_number, data in datewise_running_data.items()]
    vehicle_overtime_totals_list = [(vehicle_reg_number, total_overtime_amount) for vehicle_reg_number, total_overtime_amount in vehicle_overtime_totals.items()]
       
                 
        # Pagination
    paginator = Paginator(datewise_running_data_list, 5)  # 10 items per page

    page = request.GET.get('page')

    try:
        datewise_running_data = paginator.page(page)
    except PageNotAnInteger:
        datewise_running_data = paginator.page(1)
    except EmptyPage:
        datewise_running_data = paginator.page(paginator.num_pages)

    form = SummaryReportChartForm()
    context = {'datewise_running_data': datewise_running_data,
               'vehicle_overtime_totals_list': vehicle_overtime_totals_list,
               'form':form,
                'days': days,
                'start_date': start_date,
                'end_date': end_date,
               } 
  
    return render(request, 'vehicle/vehicle_overtime_calc.html', context)



@login_required
def vehicle_grand_summary(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None
    number_of_days = None
    vehicle_reg_number = None  
    aggregated_data = {}

    form = vehicleSummaryReportForm(request.GET or None)
    vehicle_running_data = VehicleRuniningData.objects.filter(vehicle__vehicle_rental_type='permanent')
    vehicle_fault_data = Vehiclefault.objects.filter(vehicle__vehicle_rental_type='permanent')
    vehicle_payment_data = VehicleRentalCost.objects.filter(vehicle__vehicle_rental_type='permanent')
    vehicle_ticket_data = eTicket.objects.filter(vehicle__vehicle_rental_type='permanent')
    vehicle_refill_data = FuelRefill.objects.filter(vehicle__vehicle_rental_type='permanent')
  
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        vehicle_number = form.cleaned_data.get('vehicle_number')
        
        if start_date and end_date:
            vehicle_running_data = vehicle_running_data.filter(created_at__range=(start_date, end_date))
            vehicle_fault_data = vehicle_fault_data.filter(created_at__range=(start_date, end_date))
            vehicle_payment_data = vehicle_payment_data.filter(created_at__range=(start_date, end_date))
            vehicle_ticket_data = vehicle_ticket_data.filter(created_at__range=(start_date, end_date))
            vehicle_refill_data = vehicle_refill_data.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            vehicle_running_data = vehicle_running_data.filter(created_at__range=(start_date, end_date))
            vehicle_fault_data = vehicle_fault_data.filter(created_at__range=(start_date, end_date))
            vehicle_payment_data = vehicle_payment_data.filter(created_at__range=(start_date, end_date))
            vehicle_ticket_data = vehicle_ticket_data.filter(created_at__range=(start_date, end_date))
            vehicle_refill_data = vehicle_refill_data.filter(created_at__range=(start_date, end_date))
        
        print(f"Vehicle payment data count after date filter: {vehicle_payment_data.count()}")
        for payment_data in vehicle_payment_data:
            print(f"Vehicle: {payment_data.vehicle.vehicle_reg_number}, Region: {payment_data.region}")
                 
                
        if vehicle_number:
            vehicle_running_data = vehicle_running_data.filter(vehicle__vehicle_reg_number=vehicle_number)
            vehicle_fault_data = vehicle_fault_data.filter(vehicle__vehicle_reg_number=vehicle_number)
            vehicle_payment_data = vehicle_payment_data.filter(vehicle__vehicle_reg_number=vehicle_number)
            vehicle_ticket_data = vehicle_ticket_data.filter(vehicle__vehicle_reg_number=vehicle_number)
            vehicle_refill_data = vehicle_refill_data.filter(vehicle__vehicle_reg_number=vehicle_number)

        print(f"Vehicle payment data count after vehicle number filter: {vehicle_payment_data.count()}")
        for payment_data in vehicle_payment_data:
            print(payment_data)  

        for running_data in vehicle_running_data:
            if running_data.vehicle:
                vehicle_rental_category_info = running_data.vehicle.vehicle_rental_category
                vehicle_reg_number = running_data.vehicle.vehicle_reg_number
                driver_overtime_rate = running_data.vehicle.vehicle_driver_overtime_rate
                vehicle_body_overtime_rate = running_data.vehicle.vehicle_body_overtime_rate

                total_fuel_consumed = running_data.total_fuel_consumed or 0
                total_kilometer_run = running_data.total_kilometer_run or 0

                vehicle_zone = running_data.vehicle.zone

                if vehicle_rental_category_info == 'monthly':
                    vehicle_rent = running_data.vehicle.vehicle_rent / 30
                    vehicle_rental_rate = running_data.vehicle.vehicle_rent
                elif vehicle_rental_category_info == 'daily':
                    vehicle_rent = running_data.vehicle.vehicle_rent
                    vehicle_rental_rate = running_data.vehicle.vehicle_rent
                else:
                    vehicle_rent = 0

                friday_saturday = running_data.start_time.weekday() in [4, 5]
                running_hours = running_data.running_hours or 0
                overtime_run_hours = running_hours if friday_saturday else max(0, running_hours - 8)
                overtime_cost = float(overtime_run_hours) * float(driver_overtime_rate)
                vehicle_body_overtime_cost = float(overtime_run_hours) * float(vehicle_body_overtime_rate)

                total_vehicle_bill_amount = float(vehicle_rent) + float(overtime_cost) + float(vehicle_body_overtime_cost)

                if vehicle_reg_number not in aggregated_data:
                    aggregated_data[vehicle_reg_number] = {
                        'vehicle_id': running_data.vehicle.id,
                        'total_running_hours': 0,
                        'total_overtime_run_hours': 0,
                        'total_overtime_cost': 0,
                        'total_vehicle_rent_due': 0,
                        'total_vehicle_bill_amount': 0,
                        'driver_overtime_rate': [],
                        'vehicle_body_overtime_rate': [],
                        'vehicle_rental_rate': [],
                        'vehicle_rent': [],
                        'vehicle_rental_category_info': vehicle_rental_category_info,  # Store the initial category info
                        'travel_dates': set(),
                        'num_travel_dates': 0,
                        'total_tickets_handle': 0,
                        'total_pg_runhour_handle': 0,
                        'total_fault_hours': 0,
                        'vehicle_rent_paid': 0,
                        'vehicle_body_overtime_paid': 0,
                        'vehicle_driver_overtime_paid': 0,
                        'total_bill_paid': 0,
                        'total_fuel_balance': 0,
                        'total_fuel_consumed': 0,
                        'total_kilometer_run': 0,
                        'total_kilometer_run_from_refill': 0,
                        'vehicle_body_overtime_cost': 0,
                        'total_fuel_refil': 0,
                        'total_fuel_consumed_from_refil': 0,
                        'total_fuel_balance_from_refil': 0,
                        'total_fuel_reserve_from_refil': 0,
                        'zone': vehicle_zone
                    }
                else:
                    # Ensure that the rental category info remains consistent
                    if aggregated_data[vehicle_reg_number]['vehicle_rental_category_info'] != vehicle_rental_category_info:
                        aggregated_data[vehicle_reg_number]['vehicle_rental_category_info'] = vehicle_rental_category_info

                aggregated_data[vehicle_reg_number]['total_running_hours'] += running_hours
                aggregated_data[vehicle_reg_number]['total_kilometer_run'] += total_kilometer_run
                aggregated_data[vehicle_reg_number]['total_fuel_consumed'] += total_fuel_consumed
                aggregated_data[vehicle_reg_number]['total_overtime_run_hours'] += overtime_run_hours
                aggregated_data[vehicle_reg_number]['total_overtime_cost'] += overtime_cost
                aggregated_data[vehicle_reg_number]['vehicle_body_overtime_cost'] += vehicle_body_overtime_cost
                aggregated_data[vehicle_reg_number]['total_vehicle_rent_due'] += vehicle_rent
                aggregated_data[vehicle_reg_number]['total_vehicle_bill_amount'] += float(total_vehicle_bill_amount)

                aggregated_data[vehicle_reg_number]['driver_overtime_rate'].append(driver_overtime_rate)
                aggregated_data[vehicle_reg_number]['vehicle_body_overtime_rate'].append(vehicle_body_overtime_rate)
                aggregated_data[vehicle_reg_number]['vehicle_rent'].append(vehicle_rent)
                aggregated_data[vehicle_reg_number]['vehicle_rental_rate'].append(vehicle_rental_rate)
                aggregated_data[vehicle_reg_number]['travel_dates'].add(running_data.start_time)
                aggregated_data[vehicle_reg_number]['num_travel_dates'] += 1

        for payment_data in vehicle_payment_data:
            print(payment_data)        
            if payment_data.vehicle:
                vehicle_reg_number = payment_data.vehicle.vehicle_reg_number
                total_bill_paid = payment_data.vehicle_rent_paid 
            if vehicle_reg_number in aggregated_data:
                aggregated_data[vehicle_reg_number]['total_bill_paid'] += Decimal(total_bill_paid)

          
     
        for fault_data in vehicle_fault_data:        
            if fault_data.vehicle:
                vehicle_reg_number = fault_data.vehicle.vehicle_reg_number
                if vehicle_reg_number in aggregated_data:
                    aggregated_data[vehicle_reg_number]['total_fault_hours'] += fault_data.fault_duration_hours

        for ticket_data in vehicle_ticket_data:
            if ticket_data.vehicle:
                vehicle_reg_number = ticket_data.vehicle.vehicle_reg_number
                if vehicle_reg_number in aggregated_data:
                    tt_handle = ticket_data.id
                    total_pg_runhour_handle = ticket_data.internal_generator_running_hours.total_seconds() / 3600 if isinstance(ticket_data.internal_generator_running_hours, timedelta) else ticket_data.internal_generator_running_hours
                    aggregated_data[vehicle_reg_number]['total_tickets_handle'] += 1
                    aggregated_data[vehicle_reg_number]['total_pg_runhour_handle'] += total_pg_runhour_handle

        for fuel_refill in vehicle_refill_data:
            if fuel_refill.vehicle:
                vehicle_reg_number = fuel_refill.vehicle.vehicle_reg_number
                if vehicle_reg_number in aggregated_data:
                    total_fuel_consumed_from_refil = fuel_refill.vehicle_fuel_consumed

                    total_fuel_refil = fuel_refill.refill_amount
                    total_kilometer_run_from_refill = fuel_refill.vehicle_kilometer_run or 0
                    total_fuel_balance_from_refil = total_fuel_refil - total_fuel_consumed_from_refil    

                    aggregated_data[vehicle_reg_number]['total_fuel_refil'] += total_fuel_refil
                    aggregated_data[vehicle_reg_number]['total_kilometer_run_from_refill'] += total_kilometer_run_from_refill
                    aggregated_data[vehicle_reg_number]['total_fuel_consumed_from_refil'] += total_fuel_consumed_from_refil
                    aggregated_data[vehicle_reg_number]['total_fuel_balance_from_refil'] += total_fuel_balance_from_refil

        for vehicle_reg_number, data in aggregated_data.items():
            data['total_fuel_balance'] = data['total_fuel_refil'] - data['total_fuel_consumed']

       

    aggregated_data_list = list(aggregated_data.items())
    paginator = Paginator(aggregated_data_list, 10)
    page_number = request.GET.get('page')

    try:
        aggregated_data_page = paginator.page(page_number)
    except PageNotAnInteger:
        aggregated_data_page = paginator.page(1)
    except EmptyPage:
        aggregated_data_page = paginator.page(paginator.num_pages)

    form = vehicleSummaryReportForm()
    context = {
        'aggregated_data_page': aggregated_data_page,
        'form': form,
        'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'number_of_days': number_of_days,
        'vehicle_reg_number': vehicle_reg_number
    }

    return render(request, 'vehicle/vehicle_payment_grand_sum.html', context)


  

  # ticket_data_by_vehicle = vehicle_ticket_data.values('vehicle__vehicle_reg_number').annotate(total_tickets=Count('id'))
    # for ticket_data in ticket_data_by_vehicle:
    #     vehicle_reg_number = ticket_data['vehicle__vehicle_reg_number']
    #     aggregated_data.setdefault(vehicle_reg_number, {}).setdefault('total_tickets', 0)
    #     aggregated_data[vehicle_reg_number]['total_tickets'] += ticket_data['total_tickets']


@login_required
def vehicle_detail(request, vehicle_id):
    vehicle_info = get_object_or_404(AddVehicleInfo, pk=vehicle_id)

    days = None
    start_date = None
    end_date = None
    vehicle_running_data =None
    fuel_refills = None
  
    form = VehicleDetailsForm(request.GET or {'days': 20})

    if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            days = form.cleaned_data.get('days')          

            if start_date and end_date:
                 vehicle_running_data = VehicleRuniningData.objects.filter(vehicle=vehicle_info, travel_date__range=[start_date, end_date])
                 fuel_refills = FuelRefill.objects.filter(vehicle=vehicle_info, refill_date__range=[start_date, end_date])
                 vehicle_fault = Vehiclefault.objects.filter(vehicle=vehicle_info, created_at__range=[start_date, end_date])
            elif days:
                end_date = datetime.today()
                start_date = end_date - timedelta(days=days)
                fuel_refills = FuelRefill.objects.filter(vehicle=vehicle_info, refill_date__range=[start_date, end_date])
                vehicle_running_data = VehicleRuniningData.objects.filter(vehicle=vehicle_info, travel_date__range=[start_date, end_date])
                vehicle_fault = Vehiclefault.objects.filter(vehicle=vehicle_info, created_at__range=[start_date, end_date])

    form = VehicleDetailsForm()

    return render(request, 'vehicle/view_vehicle_details.html', {
        'vehicle_info': vehicle_info,
        'vehicle_running_data': vehicle_running_data,
        'fuel_refills': fuel_refills,
        'vehicle_fault':vehicle_fault,
        'days': days,  
        'start_date': start_date,
        'end_date': end_date,
        'form':form
    })



def vehicle_run_details(request, vehicle_reg_number):
    form = SummaryReportChartForm(request.GET or {'days': 20})
    vehicle_data = VehicleRuniningData.objects.filter(vehicle__vehicle_reg_number=vehicle_reg_number)
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
 
    

    for data in vehicle_data:
        travel_data = data.start_time
        day_of_week = calendar.day_name[travel_data.weekday()]

    form=SummaryReportChartForm()
    context = {
        'vehicle_data': vehicle_data,
        'day_of_week': day_of_week,
        'form':form,
        'days':days,
    }
 
    return render(request, 'vehicle/vehicle_running_data_single.html', context)





########### Adhoc vehicle requisition and payment control mechanism #########################


def adhoc_management_dashboard(request):
    return render(request,'vehicle/adhoc_vehicle_management/adhoc_vehicle_management.html')# for expense and advance management dashboard shortcut



def create_adhoc_requisition(request):
    if request.method == 'POST':
        form = AdhocRequisitionForm(request.POST)
        if form.is_valid():
            form.instance.requester = request.user
            form.instance.requisition_id = generate_unique_finance_requisition_number()
            form.save()
            form = AdhocRequisitionForm()
            return redirect('vehicle:create_adhoc_requisition')
            
    else:
        form = AdhocRequisitionForm()
    
    adhoc_requisitions = AdhocVehicleRequisition.objects.all().order_by('-created_at')

    paginator = Paginator(adhoc_requisitions, 5)  # Show 10 requisitions per page.
    page_number = request.GET.get('page')

    try:
        adhoc_requisitions = paginator.page(page_number)
    except PageNotAnInteger:
        adhoc_requisitions = paginator.page(1)
    except EmptyPage:
        adhoc_requisitions = paginator.page(paginator.num_pages)
        
    return render(request, 'vehicle/adhoc_vehicle_management/create_adhoc_requisition.html', {
        'form': form,
        'adhoc_requisitions': adhoc_requisitions
    })






@login_required
def adhoc_approval_status(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None
    region_approvals = None
    zone_approvals = None

    form = AdhocRequisitionStatusForm(request.GET or {'days': 20})
    adhoc_requisitions = AdhocVehicleRequisition.objects.all().order_by('-created_at')

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')

        if start_date and end_date:
            adhoc_requisitions = adhoc_requisitions.filter(requisition_date__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            adhoc_requisitions = adhoc_requisitions.filter(requisition_date__range=(start_date, end_date))

        if region:
            adhoc_requisitions = adhoc_requisitions.filter(vehicle__region=region)
        if zone:
            adhoc_requisitions = adhoc_requisitions.filter(vehicle__zone=zone)
        if mp:
            adhoc_requisitions = adhoc_requisitions.filter(vehicle__mp=mp)

        # Calculate region-wise and zone-wise summaries
        region_approvals = adhoc_requisitions.values('vehicle__region').annotate(
         total_requisition=Sum('num_of_days_applied'),
        total_approved=Sum('num_of_days_approved')
            ).order_by('vehicle__region')

     

        zone_approvals = adhoc_requisitions.values('vehicle__zone').annotate(
            total_requisition=Sum('num_of_days_applied'),
            total_approved=Sum('num_of_days_approved')            
        ).order_by('vehicle__zone')
   



    # Pagination logic
    page_obj = None
    money_per_page = 20  # Adjust as needed
    paginator = Paginator(adhoc_requisitions, money_per_page)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)


  
    form = AdhocRequisitionStatusForm()
    return render(request, 'vehicle/adhoc_vehicle_management/approval_status.html', {
        'adhoc_requisitions': adhoc_requisitions,
        'page_obj': page_obj,
        'region_approvals': region_approvals,
        'zone_approvals': zone_approvals,
        'days': days,
        'form': form,
        'start_date': start_date,
        'end_date': end_date
    })



@login_required
def adhoc_approval_status2(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None
    region_approvals = None
    zone_approvals = None

    form = AdhocRequisitionStatusForm(request.GET or {'days': 20})
    adhoc_requisitions = AdhocVehicleRequisition.objects.all().order_by('-created_at')

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')

        if start_date and end_date:
            adhoc_requisitions = adhoc_requisitions.filter(requisition_date__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            adhoc_requisitions = adhoc_requisitions.filter(requisition_date__range=(start_date, end_date))

        if region:
            adhoc_requisitions = adhoc_requisitions.filter(vehicle__region=region)
        if zone:
            adhoc_requisitions = adhoc_requisitions.filter(vehicle__zone=zone)
        if mp:
            adhoc_requisitions = adhoc_requisitions.filter(vehicle__mp=mp)

        # Calculate region-wise and zone-wise summaries
        region_approvals = adhoc_requisitions.values('vehicle__region').annotate(
         total_requisition=Sum('num_of_days_applied'),
        total_approved=Sum('num_of_days_approved')
            ).order_by('vehicle__region')

     

        zone_approvals = adhoc_requisitions.values('vehicle__zone').annotate(
            total_requisition=Sum('num_of_days_applied'),
            total_approved=Sum('num_of_days_approved')            
        ).order_by('vehicle__zone')
   



    # Pagination logic
    page_obj = None
    money_per_page = 5  # Adjust as needed
    paginator = Paginator(adhoc_requisitions, money_per_page)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)


  
    form = AdhocRequisitionStatusForm()
    return render(request, 'vehicle/adhoc_vehicle_management/approval_status2.html', {
        'adhoc_requisitions': adhoc_requisitions,
        'page_obj': page_obj,
        'region_approvals': region_approvals,
        'zone_approvals': zone_approvals,
        'days': days,
        'form': form,
        'start_date': start_date,
        'end_date': end_date
    })




def manager_level_required(level):  
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.manager_level == level:
                return view_func(request, *args, **kwargs)
            else:              
                messages.warning(request, "You are not authorized to access this page.")
                return redirect('account:unauthorised_access')  
        return _wrapped_view
    return decorator



@login_required
def adhoc_management_approval(request, requisition_id):
    requisition = get_object_or_404(AdhocVehicleRequisition, id=requisition_id)
    manager_level = request.user.manager_level
    
    if requisition.level1_approval_status == 'PENDING':
        required_level = 'first_level'
    elif requisition.level2_approval_status == 'PENDING':
        required_level = 'second_level'
    elif requisition.level3_approval_status == 'PENDING':
        required_level = 'third_level'
    else:  
        return JsonResponse({"message": "Requisition already approved by all levels"}, status=400)
 
    if manager_level == required_level:
        if request.method == 'POST':
            approval_status = request.POST.get('approval_status')
            comments = request.POST.get('comments')
            num_of_days_approved = request.POST.get('num_of_days_approved')
            approval_date = timezone.now() 

            try:
                if num_of_days_approved is not None and num_of_days_approved != '':
                    num_of_days_approved = int(num_of_days_approved)
                else:
                    num_of_days_approved = 0
            except ValueError:
                messages.error(request, "Invalid approved amount")
                return redirect('vehicle:adhoc_management_approval', requisition_id=requisition_id)
            
            requisition.num_of_days_approved = num_of_days_approved
            requisition.active_status = True
            
            if required_level == 'first_level':
                requisition.level1_comments = comments
                requisition.level1_approval_status = approval_status
                requisition.level1_approval_date = approval_date
            elif required_level == 'second_level':
                requisition.level2_comments = comments
                requisition.level2_approval_status = approval_status
                requisition.level2_approval_date = approval_date
            elif required_level == 'third_level':
                requisition.level3_comments = comments
                requisition.level3_approval_status = approval_status
                requisition.level3_approval_date = approval_date
         
            requisition.save()

            return redirect('vehicle:adhoc_approval_status')
        else:
            return render(request, 'vehicle/adhoc_vehicle_management/adhoc_approval_form.html', {'requisition': requisition})
    else:        
        messages.error(request, "You cannot get access at this moment. This may be due to the previous level approval being pending or you not being authorized from your management")
        return redirect('vehicle:adhoc_approval_status')









from functools import wraps
from django.http import JsonResponse

def manager_level_required2(required_level):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.manager_level == required_level:
                return view_func(request, *args, **kwargs)
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({"message": "You are not authorized to approve this requisition."}, status=403)
                else:
                    messages.warning(request, "You are not authorized to access this page.")
                    return redirect('account:unauthorised_access')
        return _wrapped_view
    return decorator

@login_required
def adhoc_management_approval2(request, requisition_id):
    requisition = get_object_or_404(AdhocVehicleRequisition, id=requisition_id)

    # Determine the required level based on the current approval status
    if requisition.level1_approval_status == 'PENDING':
        required_level = 'first_level'
    elif requisition.level2_approval_status == 'PENDING':
        required_level = 'second_level'
    elif requisition.level3_approval_status == 'PENDING':
        required_level = 'third_level'
    else:  
        return JsonResponse({"message": "Requisition already approved by all levels"}, status=400)

    # Use the manager_level_required decorator dynamically
    @manager_level_required2(required_level)
    def process_approval(request):
        if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            approval_status = request.POST.get('approval_status')
            num_of_days_approved = request.POST.get('num_of_days_approved')
            approval_date = timezone.now()

            print(f"num_of_days_approved: {num_of_days_approved}")
            print(f"approval Status: {approval_status}")


            # Ensure num_of_days_approved is converted to the correct type if necessary
            if num_of_days_approved:
                num_of_days_approved = int(num_of_days_approved)

            if required_level == 'first_level' and requisition.level1_approval_status == 'PENDING':
                requisition.level1_approval_status = approval_status
                requisition.num_of_days_approved = num_of_days_approved
                requisition.level1_approval_date = approval_date
                requisition.active_status = True
            elif required_level == 'second_level' and requisition.level2_approval_status == 'PENDING':
                requisition.level2_approval_status = approval_status
                requisition.num_of_days_approved = num_of_days_approved
                requisition.level2_approval_date = approval_date
                requisition.active_status = True
            elif required_level == 'third_level' and requisition.level3_approval_status == 'PENDING':
                requisition.level3_approval_status = approval_status
                requisition.num_of_days_approved = num_of_days_approved
                requisition.level3_approval_date = approval_date
                requisition.active_status = True
            else:
                return JsonResponse({"message": "Invalid or already approved"}, status=400)

            requisition.save()
            return JsonResponse({"message": "Approval successful"}, status=200)

    return process_approval(request)




@login_required
def format_date(date):
    day = date.strftime('%d')
    if day.endswith(('1', '21', '31')):
        suffix = 'st'
    elif day.endswith(('2', '22')):
        suffix = 'nd'
    elif day.endswith(('3', '23')):
        suffix = 'rd'
    else:
        suffix = 'th'
    formatted_date = date.strftime(f'%d{suffix} %B %Y, %I:%M %p')
    return formatted_date



@login_required
def download_adhoc_requisition_data(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="money_requisition_data.xlsx"'

    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet()
    
    headers = ['Date','Requisition Number','Reqquester', 'Region', 'Zone','Purpose', 'Requisition Amount','Approved Amount', 'Level 1 Approval', 
               'Level 1 Approval Date', 'Level 2 Approval', 'Level 2 Approval Date', 'Level 3 Approval', 
               'Level 3 Approval Date', 'Receiving Status']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
  
    requisitions = AdhocVehicleRequisition.objects.all()
    for row, requisition in enumerate(requisitions, start=1):
        update_at_str = timezone.localtime(requisition.update_at).strftime('%Y-%m-%d %H:%M:%S')
      
        worksheet.write(row, 0, str(update_at_str))
        worksheet.write(row, 1, str(requisition.num_of_days_applied ))      
     

    workbook.close()
    return response


@login_required
def adhoc_intime(request):
    adhoc_attendance = AdhocVehicleAttendance.objects.all().order_by('-created_at')
    if request.method == 'POST':
        form = AdhocAttendanceIntimeForm(request.POST)
        if form.is_valid():
            adhoc_instance = form.save(commit=False)
            adhoc_instance.save()
            messages.success(request, 'Adhoc intime has been successfully recorded.')
            return redirect('vehicle:adhoc_intime')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = AdhocAttendanceIntimeForm()

    return render(request, 'vehicle/adhoc_vehicle_management/adhoc_intime.html', {'form': form, 'adhoc_attendance': adhoc_attendance})

@login_required
def adhoc_outtime(request, attendance_id):
    adhoc_attendance = AdhocVehicleAttendance.objects.all().order_by('-created_at')
    adhoc_instance = get_object_or_404(AdhocVehicleAttendance, id=attendance_id)
    if request.method == 'POST':
        form = AdhocAttendanceUpdateOuttimeForm(request.POST, instance=adhoc_instance)
        if form.is_valid():
            try:
                adhoc_instance = form.save(commit=False)
                if adhoc_instance.adhoc_requisition:
                    adhoc_instance.adhoc_requisition.active_status = False
                    adhoc_instance.adhoc_requisition.save()
                    print("Adhoc Requisition active_status set to False and saved.")
                adhoc_instance.save()
                messages.success(request, 'Adhoc outtime has been successfully updated.')
                return redirect('vehicle:view_adhoc_attendance')
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AdhocAttendanceUpdateOuttimeForm(instance=adhoc_instance)

    return render(request, 'vehicle/adhoc_vehicle_management/adhoc_intime.html', {'form': form, 'adhoc_instance': adhoc_instance, 'adhoc_attendance': adhoc_attendance})




@login_required
def adhoc_outtime2(request, attendance_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        adhoc_instance = get_object_or_404(AdhocVehicleAttendance, id=attendance_id)
        
        adhoc_out_date = request.POST.get('adhoc_out_date')
        adhoc_out_time = request.POST.get('adhoc_out_time')

        if adhoc_out_date and adhoc_out_time:
            try:
                adhoc_out_date = datetime.strptime(adhoc_out_date, '%Y-%m-%d').date()
                adhoc_out_time = datetime.strptime(adhoc_out_time, '%H:%M').time()

                adhoc_instance.adhoc_out_date = adhoc_out_date
                adhoc_instance.adhoc_out_time = adhoc_out_time
                
                in_datetime = datetime.combine(adhoc_instance.adhoc_in_date, adhoc_instance.adhoc_in_time)
                out_datetime = datetime.combine(adhoc_out_date, adhoc_out_time)
                adhoc_instance.adhoc_working_hours = (out_datetime - in_datetime).total_seconds() / 3600

                adhoc_instance.save()

                if adhoc_instance.adhoc_requisition:
                    adhoc_instance.adhoc_requisition.active_status = False
                    adhoc_instance.adhoc_requisition.save()

                return JsonResponse({'success': True, 'message': 'Out time successfully updated.'})

            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)})

        return JsonResponse({'success': False, 'message': 'Invalid date or time.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})


@login_required
def view_adhoc_attendance(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None
    form = AdhocRequisitionStatusForm(request.GET or None)
    adhoc_attendance_data = AdhocVehicleAttendance.objects.all().order_by('-created_at')

    for adhoc in adhoc_attendance_data:
        print(adhoc.vehicle)

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')

        if start_date and end_date:
            adhoc_attendance_data = adhoc_attendance_data.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            adhoc_attendance_data = adhoc_attendance_data.filter(created_at__range=(start_date, end_date))

        if region:
            adhoc_attendance_data = adhoc_attendance_data.filter(vehicle__region=region)
        if zone:
           adhoc_attendance_data = adhoc_attendance_data.filter(vehicle__zone=zone)
        if mp:
            adhoc_attendance_data = adhoc_attendance_data.filter(vehicle__mp=mp)


    
    # Pagination logic
    page_obj = None 
    paginator = Paginator(adhoc_attendance_data, 5)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
        
    form = AdhocRequisitionStatusForm()   
    return render(request, 'vehicle/adhoc_vehicle_management/view_adhoc_attendance.html',
             {
            'adhoc_attendance_data': adhoc_attendance_data,
            'start_date':start_date,
            'end_start':end_date,
            'days':days,
            'form':form,
            'page_obj':page_obj,

            })


@login_required
def view_adhoc_attendance2(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None
    form = AdhocRequisitionStatusForm(request.GET or None)
    adhoc_attendance_data = AdhocVehicleAttendance.objects.all().order_by('-created_at')

    for adhoc in adhoc_attendance_data:
        print(adhoc.vehicle)

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')

        if start_date and end_date:
            adhoc_attendance_data = adhoc_attendance_data.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            adhoc_attendance_data = adhoc_attendance_data.filter(created_at__range=(start_date, end_date))

        if region:
            adhoc_attendance_data = adhoc_attendance_data.filter(vehicle__region=region)
        if zone:
           adhoc_attendance_data = adhoc_attendance_data.filter(vehicle__zone=zone)
        if mp:
            adhoc_attendance_data = adhoc_attendance_data.filter(vehicle__mp=mp)


    
    # Pagination logic
    page_obj = None 
    paginator = Paginator(adhoc_attendance_data, 5)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
        
    form = AdhocRequisitionStatusForm()   
    return render(request, 'vehicle/adhoc_vehicle_management/view_adhoc_attendance2.html',
             {
            'adhoc_attendance_data': adhoc_attendance_data,
            'start_date':start_date,
            'end_start':end_date,
            'days':days,
            'form':form,
            'page_obj':page_obj,

            })


@login_required
def adhoc_summary_view(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None
    form = AdhocRequisitionStatusForm(request.GET or None)
    adhoc_summary = AdhocVehicleAttendance.objects.all()
    etickets = eTicket.objects.all() 

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        vehicle = request.GET.get('vehicle')

        if start_date and end_date:
            adhoc_summary = adhoc_summary.filter(created_at__range=(start_date, end_date))
            etickets = etickets.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            adhoc_summary = adhoc_summary.filter(created_at__range=(start_date, end_date))
            etickets = etickets.filter(created_at__range=(start_date, end_date))

        if region:
            adhoc_summary = adhoc_summary.filter(vehicle__region=region)
            etickets = etickets.filter(vehicle__region=region)
        if zone:
            adhoc_summary = adhoc_summary.filter(vehicle__zone=zone)
            etickets = etickets.filter(vehicle__zone=zone)
        if mp:
            adhoc_summary = adhoc_summary.filter(vehicle__mp=mp)
            etickets = etickets.filter(vehicle__mp=mp)
        if vehicle:
            adhoc_summary = adhoc_summary.filter(vehicle__vehicle_reg_number=vehicle)

    adhoc_summary = adhoc_summary.values(
        'vehicle__id', 'vehicle__vehicle_reg_number', 'vehicle__region', 'vehicle__zone', 'vehicle__mp'
    ).annotate( 
        total_working_hours=Sum('adhoc_working_hours'),
        total_base_bill_amount=Sum('adhoc_vehicle_base_bill_amount'),
        total_overtime_bill_amount=Sum('adhoc_vehicle_overtime_bill_amount'),
        total_adhoc_bill_amount=Sum('adhoc_vehicle_total_bill_amount'),  
                
        total_kilometer_run=Coalesce(Sum('vehicle_running_data__total_kilometer_run'), Value(0, output_field=DecimalField())), 
        total_kilometer_cost_CNG=Coalesce(Sum('vehicle_running_data__day_end_kilometer_cost_CNG'), Value(0, output_field=DecimalField())), 
        total_kilometer_cost_gasoline=Coalesce(Sum('vehicle_running_data__day_end_kilometer_cost_gasoline'), Value(0, output_field=DecimalField())),     
        total_kilometer_cost = Coalesce(Sum('vehicle_running_data__total_kilometer_cost'), Value(0, output_field=DecimalField())),

        total_fault_hours = Coalesce(Sum('vehicle_fault__fault_duration_hours'), Value(0, output_field=FloatField())),         
        adhoc_paid_amount=Coalesce(Sum('adhoc_payment__adhoc_paid_amount'), Value(0, output_field=DecimalField()))
    ).order_by('vehicle__vehicle_reg_number')

    # Fetch internal generator running hours and count for each vehicle
    vehicle_ids = [summary['vehicle__id'] for summary in adhoc_summary]
    eticket = etickets.filter(vehicle__id__in=vehicle_ids).values('vehicle__id').annotate(
        total_TT_handle=Count('id'),
        total_PGRH=ExpressionWrapper(
            Sum(F('internal_generator_running_hours')) / timedelta(seconds=1),  # Convert seconds to hours
            output_field=FloatField()
        )
    )


    # Create a dictionary for quick lookup
    eticket_dict = {item['vehicle__id']: {'total_TT_handle': item['total_TT_handle'], 'total_PGRH': item['total_PGRH']} for item in eticket}

    # Add the internal generator running hours and count to the summary
    for summary in adhoc_summary:
        summary['total_TT_handle'] = eticket_dict.get(summary['vehicle__id'], {}).get('total_TT_handle', 0)
        summary['total_PGRH'] = eticket_dict.get(summary['vehicle__id'], {}).get('total_PGRH', 0)

    # Adjust values if needed
    for summary in adhoc_summary:
        total_adhoc_bill_amount = summary['total_adhoc_bill_amount'] or Decimal('0.00')
        total_kilometer_cost = summary['total_kilometer_cost'] or Decimal('0.00')
        adhoc_paid_amount = summary['adhoc_paid_amount'] or Decimal('0.00')               
        summary['grand_total_bill_amount'] = total_adhoc_bill_amount + total_kilometer_cost
        summary['adhoc_net_payment_due'] = summary['grand_total_bill_amount'] - adhoc_paid_amount

    form = AdhocRequisitionStatusForm()
    return render(request, 'vehicle/adhoc_vehicle_management/adhoc_bill_summary.html', {
        'adhoc_summary': adhoc_summary,
        'MEDIA_URL': settings.MEDIA_URL,
        'form': form,
    })




@login_required
def create_adhoc_payment(request, adhoc_attendance_id):
    adhoc_attendance = get_object_or_404(AdhocVehicleAttendance, id=adhoc_attendance_id)
    if request.method == 'POST':
        form = AdhocPaymentForm(request.POST, request.FILES)
        if form.is_valid():
            adhoc_payment = form.save(commit=False)
            adhoc_payment.vehicle = adhoc_attendance.vehicle
            adhoc_payment.save()
            # Ensure the AdhocPayment instance is assigned to adhoc_payment
            adhoc_attendance.adhoc_payment = adhoc_payment
            adhoc_attendance.save()
            messages.success(request, 'Adhoc payment has been successfully recorded.')
            return redirect('vehicle:view_adhoc_attendance')
        else:
            messages.error(request, 'There was an error with your submission.')
    else:
       form = AdhocPaymentForm(initial={'vehicle': adhoc_attendance.vehicle})
    return render(request, 'vehicle/adhoc_vehicle_management/create_adhoc_payment.html', {'form': form, 'adhoc_attendance': adhoc_attendance})




@login_required
def adhoc_vehicle_grand_summary(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None
    number_of_days = None
    vehicle_reg_number = None  
    aggregated_data = {}
    total_kilometer_cost=None
    adhoc_vehicle_total_bill_amount = None

    form = vehicleSummaryReportForm(request.GET or {'days':60})
    vehicle_running_data = VehicleRuniningData.objects.all()
    vehicle_fault_data = Vehiclefault.objects.all()
    adhoc_vehicle_payment_data =AdhocVehiclePayment.objects.all()
    adhoc_vehicle_attendance_data =AdhocVehicleAttendance.objects.all()
    vehicle_ticket_data = eTicket.objects.all()
   
  
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        vehicle_number = form.cleaned_data.get('vehicle_number')
        
        if start_date and end_date:
            vehicle_running_data = vehicle_running_data.filter(created_at__range=(start_date, end_date),vehicle__vehicle_rental_category='daily')
            vehicle_fault_data = vehicle_fault_data.filter(created_at__range=(start_date, end_date),vehicle__vehicle_rental_category='daily')
            adhoc_vehicle_payment_data = adhoc_vehicle_payment_data.filter(created_at__range=(start_date, end_date),vehicle__vehicle_rental_category='daily')
            vehicle_ticket_data = vehicle_ticket_data.filter(created_at__range=(start_date, end_date),vehicle_vehicle__rental_category='daily')
            adhoc_vehicle_attendance_data = adhoc_vehicle_attendance_data.filter(created_at__range=(start_date, end_date),vehicle__vehicle_rental_category='daily')
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            vehicle_running_data = vehicle_running_data.filter(created_at__range=(start_date, end_date),vehicle__vehicle_rental_category='daily')
            vehicle_fault_data = vehicle_fault_data.filter(created_at__range=(start_date, end_date),vehicle__vehicle_rental_category='daily')
            adhoc_vehicle_payment_data = adhoc_vehicle_payment_data.filter(created_at__range=(start_date, end_date),vehicle__vehicle_rental_category='daily')
            vehicle_ticket_data = vehicle_ticket_data.filter(created_at__range=(start_date, end_date),vehicle__vehicle_rental_category='daily')
            adhoc_vehicle_attendance_data = adhoc_vehicle_attendance_data.filter(created_at__range=(start_date, end_date),vehicle__vehicle_rental_category='daily')
        
                        
        if vehicle_number:
            vehicle_running_data = vehicle_running_data.filter(vehicle__vehicle_reg_number=vehicle_number,vehicle__vehicle_rental_category='daily')
            vehicle_fault_data = vehicle_fault_data.filter(vehicle__vehicle_reg_number=vehicle_number,vehicle__vehicle_rental_category='daily')
            adhoc_vehicle_payment_data = adhoc_vehicle_payment_data.filter(vehicle__vehicle_reg_number=vehicle_number,vehicle__vehicle_rental_category='daily')
            vehicle_ticket_data = vehicle_ticket_data.filter(vehicle__vehicle_reg_number=vehicle_number,vehicle__vehicle_rental_category='daily')
            adhoc_vehicle_attendance_data = adhoc_vehicle_attendance_data.filter(vehicle__vehicle_reg_number=vehicle_number,vehicle__vehicle_rental_category='daily')

       
        for running_data in vehicle_running_data:
            if running_data.vehicle:
                vehicle_rental_category_info = running_data.vehicle.vehicle_rental_category
                vehicle_reg_number = running_data.vehicle.vehicle_reg_number  
                vehicle_body_overtime_rate = running_data.vehicle.vehicle_body_overtime_rate
                total_kilometer_run = running_data.total_kilometer_run or 0

                vehicle_zone = running_data.vehicle.zone
               

                total_kilometer_run = running_data.total_kilometer_run
                day_end_kilometer_cost_CNG =running_data.day_end_kilometer_cost_CNG
                day_end_kilometer_cost_gasoline =running_data.day_end_kilometer_cost_gasoline
                total_kilometer_cost = running_data.total_kilometer_cost

                if vehicle_rental_category_info == 'monthly':
                    vehicle_rent = running_data.vehicle.vehicle_rent / 30
                    vehicle_rental_rate = running_data.vehicle.vehicle_rent
                elif vehicle_rental_category_info == 'daily':
                    vehicle_rent = running_data.vehicle.vehicle_rent
                    vehicle_rental_rate = running_data.vehicle.vehicle_rent
                else:
                    vehicle_rent = 0

            

                if vehicle_reg_number not in aggregated_data:
                    aggregated_data[vehicle_reg_number] = {
                        'vehicle_id': running_data.vehicle.id,
                        'total_running_hours': 0,
                        'total_overtime_run_hours': 0,
                        'total_overtime_cost': 0,
                        'total_vehicle_rent_due': 0,
                        'total_vehicle_bill_amount': 0,
                        'driver_overtime_rate': [],
                        'vehicle_body_overtime_rate': [],

                        'vehicle_rental_rate': [],
                        'vehicle_rent': [],                       
                        'travel_dates': set(),
                        'num_travel_dates': 0,
                      
              
                        'total_fault_hours': 0,
                        'vehicle_rent_paid': 0,
                        'vehicle_body_overtime_paid': 0,
                        'vehicle_driver_overtime_paid': 0,
                      
                        'total_fuel_balance': 0,
                        'total_fuel_consumed': 0,                      
                        'total_kilometer_run_from_refill': 0,
                        'vehicle_body_overtime_cost': 0,
                        'total_fuel_refil': 0,
                        'total_fuel_consumed_from_refil': 0,
                        'total_fuel_balance_from_refil': 0,                       
                        'total_fuel_reserve_from_refil': 0,

                        'zone': vehicle_zone,
                        'vehicle_rental_category_info': vehicle_rental_category_info,  # Store the initial category info

                        'total_kilometer_run': 0,
                        'total_day_end_kilometer_cost_CNG':0,
                        'total_day_end_kilometer_cost_gasoline':0,
                        'total_kilometer_cost':0,

                        'total_adhoc_vehicle_working_hours':0,
                        'total_adhoc_vehicle_base_bill_amount':0,
                        'total_adhoc_vehicle_overtime_bill_amount':0,
                        'vehicle_working_hours_total_bill_amount':0,

                        'vehicle_grand_total_bill_amount':0,
                    
                        
                        'total_bill_paid': 0,
                        'total_payment_due':0,

                        'total_fault_hours': 0,
                        'total_tickets_handle': 0,
                        'total_pg_runhour_handle': 0,


                    }
                else:
                    # Ensure that the rental category info remains consistent
                    if aggregated_data[vehicle_reg_number]['vehicle_rental_category_info'] != vehicle_rental_category_info:
                        aggregated_data[vehicle_reg_number]['vehicle_rental_category_info'] = vehicle_rental_category_info
             
                aggregated_data[vehicle_reg_number]['total_kilometer_run'] += total_kilometer_run
                aggregated_data[vehicle_reg_number]['total_day_end_kilometer_cost_CNG'] +=day_end_kilometer_cost_CNG            
                aggregated_data[vehicle_reg_number]['total_day_end_kilometer_cost_gasoline'] += day_end_kilometer_cost_gasoline
                aggregated_data[vehicle_reg_number]['total_kilometer_cost'] += total_kilometer_cost                         
            
                aggregated_data[vehicle_reg_number]['vehicle_body_overtime_rate'].append(vehicle_body_overtime_rate)
                aggregated_data[vehicle_reg_number]['vehicle_rent'].append(vehicle_rent)
                aggregated_data[vehicle_reg_number]['vehicle_rental_rate'].append(vehicle_rental_rate)

                aggregated_data[vehicle_reg_number]['num_travel_dates'] += 1

        for payment_data in adhoc_vehicle_payment_data:      
            if payment_data.vehicle:
                vehicle_reg_number = payment_data.vehicle.vehicle_reg_number                
                total_bill_paid = payment_data.adhoc_paid_amount
            if vehicle_reg_number in aggregated_data:
                aggregated_data[vehicle_reg_number]['total_bill_paid'] += Decimal(total_bill_paid)
        
     
        for fault_data in vehicle_fault_data:        
            if fault_data.vehicle:
                vehicle_reg_number = fault_data.vehicle.vehicle_reg_number
                if vehicle_reg_number in aggregated_data:
                    aggregated_data[vehicle_reg_number]['total_fault_hours'] += fault_data.fault_duration_hours

        for ticket_data in vehicle_ticket_data:
            if ticket_data.vehicle:
                vehicle_reg_number = ticket_data.vehicle.vehicle_reg_number
                total_pg_runhour_handle = ticket_data.internal_generator_running_hours.total_seconds() / 3600 if isinstance(ticket_data.internal_generator_running_hours, timedelta) else ticket_data.internal_generator_running_hours
                if vehicle_reg_number in aggregated_data:                
                    
                    aggregated_data[vehicle_reg_number]['total_tickets_handle'] += 1
                    aggregated_data[vehicle_reg_number]['total_pg_runhour_handle'] += total_pg_runhour_handle

        for vehicle_attendance in adhoc_vehicle_attendance_data:
            if vehicle_attendance.vehicle:
                vehicle_reg_number = vehicle_attendance.vehicle.vehicle_reg_number
                if vehicle_reg_number in aggregated_data:
                    adhoc_working_hours = vehicle_attendance.adhoc_working_hours or 0
                    adhoc_vehicle_base_bill_amount = vehicle_attendance.adhoc_vehicle_base_bill_amount or 0
                    adhoc_vehicle_overtime_bill_amount = vehicle_attendance.adhoc_vehicle_overtime_bill_amount or 0
                    adhoc_vehicle_total_bill_amount = vehicle_attendance.adhoc_vehicle_total_bill_amount or 0

                    # Calculate the total grand bill and payment due
                    vehicle_grand_total_bill_amount = (adhoc_vehicle_total_bill_amount +
                                                    aggregated_data[vehicle_reg_number]['total_kilometer_cost'])
                    total_payment_due = vehicle_grand_total_bill_amount - aggregated_data[vehicle_reg_number]['total_bill_paid']

                    # Update the aggregated data
                    aggregated_data[vehicle_reg_number]['total_adhoc_vehicle_working_hours'] += adhoc_working_hours
                    aggregated_data[vehicle_reg_number]['total_adhoc_vehicle_base_bill_amount'] += adhoc_vehicle_base_bill_amount
                    aggregated_data[vehicle_reg_number]['total_adhoc_vehicle_overtime_bill_amount'] += adhoc_vehicle_overtime_bill_amount
                    aggregated_data[vehicle_reg_number]['vehicle_working_hours_total_bill_amount'] += adhoc_vehicle_total_bill_amount

                    aggregated_data[vehicle_reg_number]['vehicle_grand_total_bill_amount'] += vehicle_grand_total_bill_amount
                    aggregated_data[vehicle_reg_number]['total_payment_due'] = total_payment_due

       
    aggregated_data_list = list(aggregated_data.items())
    paginator = Paginator(aggregated_data_list, 10)
    page_number = request.GET.get('page')

    try:
        aggregated_data_page = paginator.page(page_number)
    except PageNotAnInteger:
        aggregated_data_page = paginator.page(1)
    except EmptyPage:
        aggregated_data_page = paginator.page(paginator.num_pages)

    form = vehicleSummaryReportForm()
    context = {
        'aggregated_data_page': aggregated_data_page,
        'form': form,
        'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'number_of_days': number_of_days,
        'vehicle_reg_number': vehicle_reg_number
    }

    return render(request, 'vehicle/adhoc_vehicle_management/adhoc_vehicle_grand_sum.html', context)



@login_required
def adhoc_vehicle_payment_common(request):
    if request.method == 'POST':   
        form = AdhocVehiclePaymentFormCommon(request.POST, request.FILES)
        if form.is_valid():       
            form.instance. payment_id = generate_unique_finance_requisition_number()
            form.save()
            return redirect('vehicle:adhoc_vehicle_grand_summary')
    else:     
        form =AdhocVehiclePaymentFormCommon()
    return render(request, 'vehicle/adhoc_vehicle_management/create_adhoc_payment.html', {'form': form})



def fleet_management(request):
    return render(request, 'vehicle/fleet_management.html')

