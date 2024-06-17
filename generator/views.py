from django.shortcuts import render
import xlsxwriter
import random
import calendar
import csv

from itertools import groupby
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,JsonResponse
from django.http import HttpResponseBadRequest

from django.shortcuts import render, redirect,get_object_or_404
from django.db.models import Sum, Avg,Count,Q,Case, When, IntegerField,F,Max,DurationField, DecimalField,FloatField
from django.db.models import Value,ExpressionWrapper
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal

from tickets.forms import SummaryReportChartForm
from tickets.models import eTicket
from tickets .views import generate_unique_finance_requisition_number

from vehicle.forms import vehicleSummaryReportForm

from .forms import AddPgForm,PGDatabaseViewForm,PGFuelRefillForm,UpdatePgStatusForm,UpdatePgDataBaseForm
from.forms import PGFaultRecordForm,UpdatePGFaultRecordForm,PGNumberForm
from .models import AddPGInfo,PGFuelRefill,PGFaultRecord


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from common.models import  Region, Zone, MP
from tickets.forms import SummaryReportChartForm
from dailyexpense.models import DailyExpenseRequisition





@login_required
def create_pg(request):
    pg_info = AddPGInfo.objects.all().order_by('-created_at')
    
    # Pagination logic
    paginator = Paginator(pg_info, 5)  # 5 items per page
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    if request.method == 'POST':
        form = AddPgForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.PG_add_requester = request.user
            form.instance.PG_code = generate_unique_finance_requisition_number()
            form.save()
            messages.success(request, 'PG entry created successfully!')
            return redirect('generator:view_pg_info')
    else:
        form = AddPgForm()
    
    return render(request, 'generator/create_pg.html', {'form': form, 'page_obj': page_obj})




@login_required
def update_pg_database(request, pg_PGNumber):
    pg_info= AddPGInfo.objects.get(id=pg_PGNumber)

    if request.method == 'POST': 
        form = UpdatePgDataBaseForm(request.POST, instance=pg_info)
        if form.is_valid():
            form.save()
            return redirect('generator:view_pg_info') 
    else:
        initial_data = {'PG_status': pg_info.PG_status}     
        form =UpdatePgDataBaseForm(instance=pg_info, initial=initial_data)
       
    return render(request, 'generator/update_pg.html', {'form': form,'pg_info':pg_info})


@login_required
def update_pg_status(request, pg_PGNumber):
    pg_info= AddPGInfo.objects.get(id=pg_PGNumber)  

    if request.method == 'POST': 
        form = UpdatePgStatusForm(request.POST, instance=pg_info)
        if form.is_valid():
            form.save()
            return redirect('generator:view_pg_info') 
    else:
        initial_data = {'PG_status': pg_info.PG_status}     
        form = UpdatePgStatusForm(instance=pg_info, initial=initial_data)
       
    return render(request, 'generator/update_pg.html', {'form': form,'pg_info':pg_info})





@login_required
def view_pg_info(request): 
    region = None
    zone = None
    mp = None
    PGNumber = None

    form = PGDatabaseViewForm(request.GET)

    pg_info = AddPGInfo.objects.all().order_by('-created_at')

    if form.is_valid():      
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        PGNumber = form.cleaned_data.get('PGNumber')

        if region:
             pg_info = pg_info.filter(region__name=region)
        if zone:
             pg_info = pg_info.filter(zone__name=zone)
        if mp:
             pg_info = pg_info.filter(mp__name=mp)

        if PGNumber:
               pg_info = pg_info.filter(PGNumber= PGNumber)

    # Pagination logic
    page_obj = None
    pg_per_page = 3
    paginator = Paginator(pg_info, pg_per_page)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    form = PGDatabaseViewForm()
    return render(request, 'generator/view_pg_info.html', {
        'pg_info': pg_info,
        'page_obj': page_obj,
        'form': form,       
        'region': region,
        'zone': zone,
        'mp': mp,
        'page_obj':page_obj
    })





@login_required
def add_pg_fuel2(request):
    if request.method == 'POST':   
        form = PGFuelRefillForm(request.POST, request.FILES)
        if form.is_valid():        
            form.instance.refill_requester= request.user
            form.instance.fuel_refill_code = generate_unique_finance_requisition_number()
            form.save()
            return redirect('generator:view_pg_fuel')
    else:     
        form = PGFuelRefillForm()
    return render(request, 'generator/add_pg_fuel.html', {'form': form})




@login_required
def add_pg_fuel(request):
    if request.method == 'POST':   
        form = PGFuelRefillForm(request.POST, request.FILES)
        if form.is_valid():
            pg_number = form.cleaned_data.get('pgnumber')  # Assuming the form has a field for PG number
            try:
                pg_instance = AddPGInfo.objects.get(PGNumber=pg_number)
                if pg_instance.PG_status == 'faulty':
                    messages.error(request, f'Thiss is a faulty PG: {pg_number} and you can not refil faulty PG. If the PG is repaired then pls update PG database first and then try again')
                else:
                    form.instance.refill_requester = request.user
                    form.instance.fuel_refill_code = generate_unique_finance_requisition_number()
                    form.save()
                    messages.success(request, f'Fuel refilled successfully for PG: {pg_number}')
                    return redirect('generator:view_pg_fuel')
            except AddPGInfo.DoesNotExist:
                messages.error(request, f'PG: {pg_number} does not exist')
    else:
        form = PGFuelRefillForm()
    return render(request, 'generator/add_pg_fuel.html', {'form': form})



@login_required
def view_pg_fuel(request):
    pg_info = PGFuelRefill.objects.all().order_by('-created_at')

    # CSV download logic
    if 'download_csv' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="expense_approval_status.csv"'
        writer = csv.writer(response)
        writer.writerow(['created_at', 'Requester'])

        for expense_requisition in pg_info:
            writer.writerow([
                expense_requisition.created_at,
                expense_requisition.refill_requester,
            ])
        return response

    # Pagination logic
    pg_per_page = 10
    paginator = Paginator(pg_info, pg_per_page)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    form = PGDatabaseViewForm()
    return render(request, 'generator/view_pg_fuel.html', {
        'pg_info': pg_info,
        'page_obj': page_obj,
        'form': form,
    })


@login_required
def pg_summary_report(request):
    form = vehicleSummaryReportForm(request.GET or {'days': 20})
    tickets = eTicket.objects.all().order_by('-created_at')  
    pg_fuel_refill = PGFuelRefill.objects.all()
    pgfuel_advance_from_daily_expense = DailyExpenseRequisition.objects.all()

    pg_summary_reports = {} 
    processed_pg = {}
    days = None
    start_date = None
    end_date = None
    fuel_consumed_per_run_hour = 0
    total_fuel_cost = 0

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')

        if start_date and end_date:
            tickets = tickets.filter(created_at__range=(start_date, end_date))
            pg_fuel_refill = pg_fuel_refill.filter(created_at__range=(start_date, end_date))
            pgfuel_advance_from_daily_expense = pgfuel_advance_from_daily_expense.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            tickets = tickets.filter(created_at__range=(start_date, end_date))
            pg_fuel_refill = pg_fuel_refill.filter(created_at__range=(start_date, end_date))
            pgfuel_advance_from_daily_expense = pgfuel_advance_from_daily_expense.filter(created_at__range=(start_date, end_date))

        if region:
            tickets = tickets.filter(region=region)
            pg_fuel_refill = pg_fuel_refill.filter(region=region)
            pgfuel_advance_from_daily_expense = pgfuel_advance_from_daily_expense.filter(region=region)
        if zone:
            tickets = tickets.filter(zone=zone)
            pg_fuel_refill = pg_fuel_refill.filter(zone=zone)
            pgfuel_advance_from_daily_expense = pgfuel_advance_from_daily_expense.filter(zone=zone)
        if mp:
            tickets = tickets.filter(mp=mp)
            pg_fuel_refill = pg_fuel_refill.filter(mp=mp)
            pgfuel_advance_from_daily_expense = pgfuel_advance_from_daily_expense.filter(mp=mp)

        for data in tickets:
            region = data.region
            zone = data.zone

            # Handle missing AddPGInfo
            try:
                pgnumber = data.pgnumber
            except AddPGInfo.DoesNotExist:
                continue  # Skip this iteration if AddPGInfo does not exist

            if pgnumber in processed_pg:
                continue

            processed_pg[pgnumber] = data

            if region not in pg_summary_reports:
                pg_summary_reports[region] = {}
            if zone not in pg_summary_reports[region]:
                pg_summary_reports[region][zone] = {}
            if pgnumber not in pg_summary_reports[region][zone]:
                pg_summary_reports[region][zone][pgnumber] = {
                    'total_refill_amount': 0,
                    'total_fuel_others_purchase': 0,
                    'total_fuel_cash_advance_taken': 0,
                    'total_fuel_cash_advance': 0,
                    'total_tt_handle': 0,
                    'total_run_hour': 0,
                    'total_fuel_cost': 0,
                    'fuel_consumed_per_tt': 0,
                    'fuel_consumed_per_run_hour': 0,
                }

            pgfuel_advance_from_daily_expense = pgfuel_advance_from_daily_expense.filter(pgnumber=pgnumber, purpose='pg_local_fuel_purchase')
            total_fuel_cash_advance_taken = pgfuel_advance_from_daily_expense.aggregate(total_fuel_cash_advance_taken=Sum('requisition_amount'))['total_fuel_cash_advance_taken'] or 0

            related_refills = pg_fuel_refill.filter(pgnumber=data.pgnumber)

            total_refill_amount = related_refills.aggregate(total_refill_amount=Sum('refill_amount'))['total_refill_amount'] or 0

            others_refills = related_refills.filter(fuel_supplier_name='Others')
            total_fuel_others_purchase = others_refills.aggregate(total_refill_amount=Sum('refill_amount'))['total_refill_amount'] or 0

            total_fuel_cost = related_refills.aggregate(total_fuel_cost=Sum('fuel_cost'))['total_fuel_cost'] or 0

            total_tt_handle = tickets.filter(pgnumber=data.pgnumber).aggregate(total_tt_handle=Count('internal_ticket_number'))['total_tt_handle'] or 0
            total_run_hour = tickets.filter(pgnumber=data.pgnumber).aggregate(total_run_hour=Sum(F('internal_generator_running_hours')))['total_run_hour'] or timedelta(0)
            total_run_hour_seconds = total_run_hour.total_seconds() if isinstance(total_run_hour, timedelta) else 0
            total_run_hour_hours = total_run_hour_seconds / 3600
            fuel_consumed_per_tt = total_fuel_cost / total_tt_handle

            if total_run_hour_hours != 0:
                fuel_consumed_per_run_hour = float(total_refill_amount) / float(total_run_hour_hours)
            else:
                fuel_consumed_per_run_hour = 0

            pg_summary_reports[region][zone][pgnumber]['total_refill_amount'] += total_refill_amount
            pg_summary_reports[region][zone][pgnumber]['total_fuel_others_purchase'] += total_fuel_others_purchase
            pg_summary_reports[region][zone][pgnumber]['total_fuel_cash_advance_taken'] += total_fuel_cash_advance_taken
            pg_summary_reports[region][zone][pgnumber]['total_fuel_cost'] += total_fuel_cost
            pg_summary_reports[region][zone][pgnumber]['total_tt_handle'] += total_tt_handle
            pg_summary_reports[region][zone][pgnumber]['total_run_hour'] += total_run_hour_hours
            pg_summary_reports[region][zone][pgnumber]['fuel_consumed_per_tt'] += fuel_consumed_per_tt
            pg_summary_reports[region][zone][pgnumber]['fuel_consumed_per_run_hour'] += fuel_consumed_per_run_hour

    paginator = Paginator(list(pg_summary_reports.items()), 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    form = vehicleSummaryReportForm()
    return render(request, 'generator/pg_summary_report.html', {
        'pg_summary_reports': page_obj,  # Pass the paginated object
        'form': form,
        'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'region': region,
        'zone': zone,
        'mp': mp,
    })



@login_required
def faulty_pg_report(request):
    total_pg = AddPGInfo.objects.aggregate(total_pg=Count("id"))
    total_good_pg = AddPGInfo.objects.filter(PG_status='good').aggregate(total_good_pg=Count("id"))
    total_faulty_pg = AddPGInfo.objects.filter(PG_status='faulty').aggregate(total_faulty_pg=Count("id"))
 
    total_pg_count = total_pg['total_pg']
    total_good_pg_count = total_good_pg['total_good_pg']
    total_faulty_pg_count = total_faulty_pg['total_faulty_pg']
    faulty_pg_percentage =  total_faulty_pg_count / total_pg_count * 100

    zonewise_report = AddPGInfo.objects.values('region', 'zone').annotate(
        total_count=Count('id'),
        good_count=Count('id', filter=Q(PG_status='good')),
        faulty_count=Count('id', filter=Q(PG_status='faulty')),
        faulty_percentage=Case(
            When(total_count__gt=0, then=ExpressionWrapper((F('faulty_count') / F('total_count')) * 100, output_field=FloatField())),
            default=Value(0),
            output_field=FloatField()
        )
    )
    

    zonewise_data = []
    for entry in zonewise_report:
        region = entry['region']
        zone = entry['zone']
        faulty_percentage = (entry['faulty_count'] / entry['total_count']) * 100 if entry['total_count'] > 0 else 0
        zonewise_data.append({
            'region': region,
            'zone': zone,
            'total_count': entry['total_count'],
            'good_count': entry['good_count'],
            'faulty_count': entry['faulty_count'],
            'faulty_percentage': faulty_percentage,
        })
  
       
    report = AddPGInfo.objects.values('PG_supplier', 'region', 'zone', 'mp').annotate(
        total_count=Count('id'),
        good_count=Count('id', filter=Q(PG_status='good')),
        faulty_count=Count('id', filter=Q(PG_status='faulty'))
    )

    report_data = {}
    for entry in report:
        supplier = entry['PG_supplier']
        entry['faulty_percentage'] = (entry['faulty_count'] / entry['total_count']) * 100 if entry['total_count'] > 0 else 0
        if supplier not in report_data:
            report_data[supplier] = {
                'entries': [],
                'total_good_count': 0,
                'total_faulty_count': 0,
                'total_count': 0
            }
        report_data[supplier]['entries'].append(entry)
        report_data[supplier]['total_good_count'] += entry['good_count']
        report_data[supplier]['total_faulty_count'] += entry['faulty_count']
        report_data[supplier]['total_count'] += entry['total_count']

    return render(request, 'generator/faulty_pg_report.html', 
                  {'report_data': report_data,
                   'total_pg_count':total_pg_count,
                   'total_faulty_pg_count':total_faulty_pg_count,
                    'total_good_pg_count':total_good_pg_count,
                    'faulty_pg_percentage':faulty_pg_percentage,
                     'zonewise_data': zonewise_data,
                     })


@login_required
def create_pg_fault_record(request):
    if request.method == 'POST':
        print("POST data:", request.POST)  # Debug print
        form = PGFaultRecordForm(request.POST)
        if form.is_valid():
            pg_fault_record = form.save(commit=False)
            pg_fault_record.pg_fault_code = generate_unique_finance_requisition_number()
            pg_fault_record.save()

            pg_info = pg_fault_record.pgnumber
            if pg_info.PG_status != 'faulty':
                pg_info.PG_status = 'faulty'
                pg_info.save()
            return redirect('generator:view_pg_fault')
        else:
            print("Form is not valid:", form.errors)  # Debug print
    else:
        form = PGFaultRecordForm()
    
    return render(request, 'generator/pg_fault_record.html', {'form': form})


@login_required
def update_pg_fault_record(request, pg_id):
    pg_fault_instance = get_object_or_404(PGFaultRecord, id=pg_id)
    if request.method == 'POST':          
        form = UpdatePGFaultRecordForm(request.POST, instance=pg_fault_instance)    
        if form.is_valid():
            updated_pg_fault_record = form.save()
            # form.save()
            pg_info = updated_pg_fault_record.pgnumber
            if pg_info and pg_info.PG_status != 'good':
                pg_info.PG_status = 'good'
                pg_info.save()  # Save the updated PG status
            return redirect('generator:view_pg_fault') 
    else:
        form = UpdatePGFaultRecordForm(instance=pg_fault_instance)        
    return render(request, 'generator/pg_fault_record_update.html', {'form': form, 'pg_fault_instance': pg_fault_instance})



def view_pg_fault(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None
    
    form = SummaryReportChartForm(request.GET or {'days': 20})
    pg_fault_data = PGFaultRecord.objects.all().order_by('-created_at')
    
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        
        if start_date and end_date:
            pg_fault_data =  pg_fault_data.filter(created_at__range=(start_date, end_date))
            if region:
                pg_fault_data = pg_fault_data.filter(region=region)
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            pg_fault_data =  pg_fault_data.filter(created_at__range=(start_date, end_date))
          
        if region:
             pg_fault_data =  pg_fault_data.filter(region__name=region)
        if zone:
            pg_fault_data = pg_fault_data.filter(zone__name=zone)
        if mp:
           pg_fault_data = pg_fault_data.filter(mp__name=mp)
    form = SummaryReportChartForm()
    return render(request,'generator/pg_fault_record_view .html', 
                  {'pg_fault_data':pg_fault_data,
                   'form':form,
                   'days':days,
                   'start_date':start_date,
                   'end_date':end_date,
                   'region':region,
                   'zone':zone,
                   'mp':mp
                   })


@login_required
def view_pg_details_fault(request):
    pg_details = None
    if request.method == 'POST':
        form = PGNumberForm(request.POST)
        if form.is_valid():
            pg_number = form.cleaned_data['pg_number']
            pg_info = get_object_or_404(AddPGInfo, PGNumber=pg_number)
            pg_details = PGFaultRecord.objects.filter(pgnumber=pg_info)
    else:
        form = PGNumberForm()

    return render(request, 'generator/pg_fault_record_details.html', {'form': form, 'pg_details': pg_details})




def pg_management(request):
    return render(request, 'generator/pg_management.html') # for pg management dashboard

