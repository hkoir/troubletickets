
import xlsxwriter
import random

from itertools import groupby
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,JsonResponse

from django.shortcuts import render, redirect,get_object_or_404
from django.db.models import Sum, Avg,Count,Q,Case, When, IntegerField,F,Max,DurationField, DecimalField,FloatField
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
from.forms import vehicleSummaryReportForm

import csv







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
    vehicle_expenses = VehicleRuniningData.objects.all()
    paginator = Paginator(vehicle_expenses, 10) 
    page_number = request.GET.get('page')

    try:
        vehicle_expenses = paginator.page(page_number)
    except PageNotAnInteger:
        vehicle_expenses = paginator.page(1)
    except EmptyPage:
        vehicle_expenses = paginator.page(paginator.num_pages)

    return render(request, 'vehicle/view_vehicle_travel_data.html', {'vehicle_expenses': vehicle_expenses})




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
    fuel_refill = FuelRefill.objects.all().order_by('-created_at')

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

    return render(request, 'vehicle/view_fuel_refill.html', {'fuel_refill':fuel_refill})




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
    vehicle_payment_data = VehicleRentalCost.objects.all()   
    return render(request, 'vehicle/view_vehicle_payment.html', {'vehicle_payment_data': vehicle_payment_data})



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
def view_vehicle_fault(request):
    vehiclefault = Vehiclefault.objects.all()   
    return render(request, 'vehicle/view_vehicle_fault.html', {'vehiclefault': vehiclefault})

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
                'total_kilometer_run_from_running_data':0
            }

        total_refill_amount = total_refill_amount_qs.filter(vehicle__vehicle_reg_number=data.vehicle.vehicle_reg_number).aggregate(total_refill_amount=Sum('refill_amount'))['total_refill_amount'] or 0
        total_kilometer_run_from_refill_data = total_refill_amount_qs.filter(vehicle__vehicle_reg_number=data.vehicle.vehicle_reg_number).aggregate( total_kilometer_run_from_refill_data=Sum('vehicle_kilometer_run'))['total_kilometer_run_from_refill_data'] or 0
        
        total_kilometer_run_from_running_data = vehicle_running_data.filter(region=region, zone=zone, vehicle=data.vehicle).aggregate(total_kilometer_run_from_running_data =Sum('total_kilometer_run'))['total_kilometer_run_from_running_data'] or 0
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


## vehicle cost performance #######################
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

    form = vehicleSummaryReportForm(request.GET or {'days': 20})
    vehicle_running_data = VehicleRuniningData.objects.all()
    vehicle_fault_data = Vehiclefault.objects.all()
    vehicle_payment_data = VehicleRentalCost.objects.all()
    vehicle_ticket_data = eTicket.objects.all()
    vehicle_refill_data = FuelRefill.objects.all()

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')

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

        if region:
            vehicle_running_data = vehicle_running_data.filter(region=region)
            vehicle_fault_data = vehicle_fault_data.filter(region=region)
            vehicle_payment_data = vehicle_payment_data.filter(region=region)
            vehicle_ticket_data = vehicle_ticket_data.filter(region=region)
            vehicle_refill_data = vehicle_refill_data.filter(region=region)
        if zone:
            vehicle_running_data = vehicle_running_data.filter(zone=zone)
            vehicle_fault_data = vehicle_fault_data.filter(zone=zone)
            vehicle_payment_data = vehicle_payment_data.filter(zone=zone)
            vehicle_ticket_data = vehicle_ticket_data.filter(zone=zone)
            vehicle_refill_data = vehicle_refill_data.filter(zone=zone)
        if mp:
            vehicle_running_data = vehicle_running_data.filter(mp=mp)
            vehicle_fault_data = vehicle_fault_data.filter(mp=mp)
            vehicle_payment_data = vehicle_payment_data.filter(mp=mp)
            vehicle_ticket_data = vehicle_ticket_data.filter(mp=mp)
            vehicle_refill_data = vehicle_refill_data.filter(mp=mp)

        for running_data in vehicle_running_data:
            if running_data.vehicle:
                vehicle_reg_number = running_data.vehicle.vehicle_reg_number
                driver_overtime_rate = running_data.vehicle.vehicle_driver_overtime_rate
                vehicle_body_overtime_rate = running_data.vehicle.vehicle_body_overtime_rate      

                total_fuel_consumed = running_data.total_fuel_consumed or 0
                total_kilometer_run = running_data.total_kilometer_run or 0

                vehicle_zone = running_data.vehicle.zone

                if running_data.vehicle.vehicle_rental_category == 'monthly':
                    vehicle_rent = running_data.vehicle.vehicle_rent / 30
                    vehicle_rental_type = 'Monthly'
                elif running_data.vehicle.vehicle_rental_category == 'daily':
                    vehicle_rent = running_data.vehicle.vehicle_rent
                    vehicle_rental_type = 'Daily'
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
                        'total_vehicle_bill_amount':0,
                        'driver_overtime_rate': [],
                        'vehicle_body_overtime_rate':[],
                        'vehicle_rent': [],
                        'vehicle_rental_type': set(),
                        'travel_dates': set(),
                        'num_travel_dates': 0,
                        'total_tickets_handle': 0,
                        'total_pg_runhour_handle': 0,
                        'total_fault_hours': 0,

                        'vehicle_rent_paid': 0,
                        'vehicle_body_overtime_paid': 0,
                        'vehicle_driver_overtime_paid': 0,
                        'total_bill_paid':0,
                    
                        'total_fuel_balance':0,
                        'total_fuel_consumed':0,
                        'total_kilometer_run':0,
                        'total_kilometer_run_from_refill':0,
                        'vehicle_body_overtime_cost':0,

                        'total_fuel_refil':0,
                        'total_fuel_consumed_from_refil':0,
                        'total_fuel_balance_from_refil':0,
                        'total_fuel_reserve_from_refil':0,
                        'zone': vehicle_zone 
                    }

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
                aggregated_data[vehicle_reg_number]['vehicle_rental_type'].add(vehicle_rental_type)
                aggregated_data[vehicle_reg_number]['travel_dates'].add(running_data.start_time)
                aggregated_data[vehicle_reg_number]['num_travel_dates'] += 1

        for fault_data in vehicle_fault_data:
            if fault_data.vehicle:
                vehicle_reg_number = fault_data.vehicle.vehicle_reg_number  # Ensure we get the correct vehicle registration number     
                if vehicle_reg_number in aggregated_data:  # Check if vehicle_reg_number is in aggregated_data
                    aggregated_data[vehicle_reg_number]['total_fault_hours'] += fault_data.fault_duration_hours

        for payment_data in vehicle_payment_data:
            if payment_data.vehicle:
                vehicle_reg_number = payment_data.vehicle.vehicle_reg_number  # Ensure we get the correct vehicle registration number   
                if vehicle_reg_number in aggregated_data:  # Check if vehicle_reg_number is in aggregated_data
                    total_bill_paid = float(payment_data.vehicle_rent_paid) + float(payment_data.vehicle_body_overtime_paid) + float(payment_data.vehicle_driver_overtime_paid)
                    aggregated_data[vehicle_reg_number]['vehicle_rent_paid'] += float(payment_data.vehicle_rent_paid)
                    aggregated_data[vehicle_reg_number]['vehicle_body_overtime_paid'] += float(payment_data.vehicle_body_overtime_paid)
                    aggregated_data[vehicle_reg_number]['vehicle_driver_overtime_paid'] += float(payment_data.vehicle_driver_overtime_paid)
                    aggregated_data[vehicle_reg_number]['total_bill_paid'] += float(total_bill_paid)

        for ticket_data in vehicle_ticket_data:
            if ticket_data.vehicle:
                vehicle_reg_number = ticket_data.vehicle.vehicle_reg_number  # Ensure we get the correct vehicle registration number
                if vehicle_reg_number in aggregated_data:  # Check if vehicle_reg_number is in aggregated_data
                    total_pg_runhour_handle = ticket_data.internal_generator_running_hours.total_seconds() / 3600 if isinstance(ticket_data.internal_generator_running_hours, timedelta) else ticket_data.internal_generator_running_hours
                    aggregated_data[vehicle_reg_number]['total_tickets_handle'] += 1
                    aggregated_data[vehicle_reg_number]['total_pg_runhour_handle'] += total_pg_runhour_handle

        for fuel_refill in vehicle_refill_data:
            if fuel_refill.vehicle:
                vehicle_reg_number = fuel_refill.vehicle.vehicle_reg_number  # Ensure we get the correct vehicle registration number
                if vehicle_reg_number in aggregated_data:  # Check if vehicle_reg_number is in aggregated_data
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

        for vehicle_reg_number, data in aggregated_data.items():
            vehicle_rental_types = data.get('vehicle_rental_type', set())
            data['vehicle_rental_type'] = ', '.join(vehicle_rental_types)

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
            elif days:
                end_date = datetime.today()
                start_date = end_date - timedelta(days=days)
                fuel_refills = FuelRefill.objects.filter(vehicle=vehicle_info, refill_date__range=[start_date, end_date])
                vehicle_running_data = VehicleRuniningData.objects.filter(vehicle=vehicle_info, travel_date__range=[start_date, end_date])

    form = VehicleDetailsForm()

    return render(request, 'vehicle/view_vehicle_details.html', {
        'vehicle_info': vehicle_info,
        'vehicle_running_data': vehicle_running_data,
        'fuel_refills': fuel_refills,
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




def fleet_management(request):
    return render(request, 'vehicle/fleet_management.html')