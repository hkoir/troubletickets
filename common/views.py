from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import FuelPumpDatabaseForm
from tickets .views import generate_unique_finance_requisition_number
from django.shortcuts import render, redirect,get_object_or_404
from django.db.models import Sum, Avg,Count,Q,Case, When, IntegerField,F,Max,DurationField, DecimalField,ExpressionWrapper
import random,json,uuid,base64,csv

import pandas as pd
from.forms import PGRForm
from tickets.views import generate_unique_ticket_number

from datetime import datetime,timedelta
from.forms import PGRViewForm,ExcelUploadForm
from.models import FuelPumpDatabase,PGRdatabase,Notice,PGTLdatabase,fuelPumpPayment
from.forms import viewFuelPumpForm,NoticeForm,PGTLForm

from dailyexpense.views import manager_level_required
from collections import defaultdict

from vehicle.models import FuelRefill
from generator.models import PGFuelRefill
from .forms import FuelWithdrawForm,FuelPumpPaymentForm,FuelPumpSearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from vehicle.models import AdhocVehicleAttendance
from adhocman.models import AdhocAttendance
from dailyexpense.models import DailyExpenseRequisition,MoneyRequisition
from billable.models import CivilPower
from.forms import AllExpenseForm
from tickets.models import eTicket


@manager_level_required('first_level')
@login_required
def add_notice(request):
    if request.method == 'POST':
        form = NoticeForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('common:view_notices')
    else:
        form = NoticeForm()
    return render(request, 'common/add_notice.html', {'form': form})


@login_required
def view_notices(request):
    notices = Notice.objects.all().order_by('-created_at')
    form = NoticeForm()
    return render(request, 'common/view_notices.html', {'notices': notices, 'form': form})


##################### Fuel pump database ###############################################
@login_required
def create_fuel_pump_database(request):
    if request.method == 'POST':
        form = FuelPumpDatabaseForm(request.POST,request.FILES)
        if form.is_valid():
            pump_record = form.save(commit=False) 
            pump_record.fuel_pump_id = generate_unique_finance_requisition_number()
            pump_record.save()  
            form.save()
            messages.success(request, "Entries created successfully")
            return redirect('common:view_fuel_pump')
    else:
        form = FuelPumpDatabaseForm()
    return render(request, 'common/create_fuel_pump.html', {'form': form})


def view_fuel_pump(request):
    pump_data = FuelPumpDatabase.objects.all().order_by('-created_at')    
    form = viewFuelPumpForm(request.GET or None)
    if form.is_valid():
        region= form.cleaned_data.get('region')
        zone=form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        fuel_pump_name = form.cleaned_data.get('fuel_pump_name')  
        if region:
            pump_data = pump_data.filter(region=region)
        if zone:
            pump_data = pump_data.filter(zone=zone)
        if mp:
            pump_data = pump_data.filter(mp=mp)
        if fuel_pump_name:
            pump_data = pump_data.filter(fuel_pump_name = fuel_pump_name)
    else:
        form=viewFuelPumpForm()
    page_obj = None 
    paginator = Paginator(pump_data, 6)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    form=viewFuelPumpForm()                   
    return render(request,'common/view_fuel_pump_database.html',
        {'pump_data':pump_data,
         'form':form,
         'page_obj':page_obj

         })



def update_fuel_pump_database(request, pump_id):
    pump_instance = get_object_or_404(FuelPumpDatabase, id=pump_id)
    if request.method == 'POST':
        form = FuelPumpDatabaseForm(request.POST, request.FILES, instance=pump_instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Entries updated successfully")
            return redirect('common:view_fuel_pump')
    else:
        form = FuelPumpDatabaseForm(instance=pump_instance)
    return render(request, 'common/create_fuel_pump.html', {'form': form, 'pump_instance': pump_instance})


################## PGR PGTL database ######################################################
def create_pgr(request):
    if request.method == 'POST':
        form = PGRForm(request.POST,request.FILES)
        if form.is_valid():
            pgr_record = form.save(commit=False) 
            pgr_record.pgr_id = generate_unique_ticket_number() 
            pgr_record.save()  
            form.save()
            messages.success(request, "Entries created successfully")
            return redirect('common:view_pgr_database')  # Replace 'success_page' with the name of your success page
    else:
        form = PGRForm()
    return render(request, 'common/create_pgr.html', {'form': form})


def create_pgtl(request):
    if request.method == 'POST':
        form = PGTLForm(request.POST,request.FILES)
        if form.is_valid():
            pgtl_record = form.save(commit=False) 
            pgtl_record.pgtl_id = generate_unique_ticket_number() 
            pgtl_record.save()  
            form.save()
            messages.success(request, "Entries created successfully")
            return redirect('common:view_pgr_database')  # Replace 'success_page' with the name of your success page
    else:
        form = PGTLForm()
    return render(request, 'common/create_pgtl.html', {'form': form})



def view_pgr_database(request):  
    start_date=None
    end_date=None
    days=None
    pgr_name = None  
    form = PGRViewForm(request.GET or None)
    pgr_list = PGRdatabase.objects.all().order_by('-created_at')    
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        pgr_name = form.cleaned_data.get('pgr')        
        if start_date and end_date:
            pgr_list = pgr_list.filter(created_at__range=(start_date, end_date))
            if region:
                pgr_list = pgr_list.filter(region=region)
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            pgr_list = pgr_list.filter(created_at__range=(start_date, end_date))
          
        if region:
            pgr_list = pgr_list.filter(region=region)
        if zone:
            pgr_list = pgr_list.filter(zone=zone)
        if mp:
            pgr_list = pgr_list.filter(mp=mp)

        if pgr_name:
            pgr_list = pgr_list.filter(name=pgr_name)
    else:
        form = PGRViewForm()

    page_obj = None 
    paginator = Paginator(pgr_list, 6)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    form = PGRViewForm()
    return render(request,'common/view_pgr_database.html',
        {
        'pgr_list':pgr_list,
        'form':form,
        'days':days,
        'start_date':start_date,
        'end_date':end_date,
        'page_obj':page_obj
        })


def update_pgr_database(request, pgr_id):
    pgr_instance = get_object_or_404(PGRdatabase, id=pgr_id)
    if request.method == 'POST':
        form = PGRForm(request.POST, request.FILES, instance=pgr_instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Entries updated successfully")
            return redirect('common:view_pgr_database')  # Replace 'success_page' with the name of your success page
    else:
        form = PGRForm(instance=pgr_instance)
    return render(request, 'common/update_pgr_database.html', {'form': form, 'pgr_instance': pgr_instance})


def update_pgtl_database(request, pgtl_id):
    pgtl_instance = get_object_or_404(PGTLdatabase, id=pgtl_id)
    if request.method == 'POST':
        form = PGTLForm(request.POST, request.FILES, instance=pgtl_instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Entries updated successfully")
            return redirect('common:view_pgr_database')  # Replace 'success_page' with the name of your success page
    else:
        form = PGTLForm(instance=pgtl_instance)
    return render(request, 'common/update_pgtl_database.html', {'form': form, 'pgtl_instance': pgtl_instance})


def pgr_summary_view2(request):   
    summary_data = PGRdatabase.objects.values('region', 'zone', 'mp').annotate(
        total_pgr=Count('id', filter=Q(PGR_type='PGR')),
        total_pgtl=Count('id', filter=Q(PGR_type='PGTL'))
    ).order_by('region', 'zone', 'mp')
    overall_summary = PGRdatabase.objects.aggregate(
        total_pgr=Count('id', filter=Q(PGR_type='PGR')),
        total_pgtl=Count('id', filter=Q(PGR_type='PGTL'))
    )
    return render(request, 'common/summary_pgr.html', 
            {
            'summary_data': summary_data,
            'overall_summary':overall_summary
            })


def pgr_summary_view(request):
    PGR_summary_data = PGRdatabase.objects.values('region', 'zone', 'mp').annotate(
        total_pgr=Count('id'),
        total_adhoc_pgr = Count('id',filter=Q(PGR_category ='adhoc')),
        total_permanent_pgr = Count('id',filter=Q(PGR_category ='permanent'))
    ).order_by('region', 'zone', 'mp')
    PGTL_summary_data = PGTLdatabase.objects.values('region', 'zone', 'mp').annotate(
        total_pgtl=Count('id')
    ).order_by('region', 'zone', 'mp') 
    combined_summary_data = defaultdict(lambda: {'total_pgr': 0, 'total_pgtl': 0,'total_adhoc_pgr':0,'total_permanent_pgr':0})
    for item in PGR_summary_data:
        key = (item['region'], item['zone'], item['mp'])
        combined_summary_data[key]['total_pgr'] = item['total_pgr']
        combined_summary_data[key]['total_adhoc_pgr'] = item['total_adhoc_pgr']
        combined_summary_data[key]['total_permanent_pgr'] = item['total_permanent_pgr']
    for item in PGTL_summary_data:
        key = (item['region'], item['zone'], item['mp'])
        combined_summary_data[key]['total_pgtl'] = item['total_pgtl']
    pgr_overall_summary = PGRdatabase.objects.aggregate(
        total_pgr=Count('id')
    )
    pgtl_overall_summary = PGTLdatabase.objects.aggregate(
        total_pgtl=Count('id')
    )

    return render(request, 'common/summary_pgr.html', 
        {
            'combined_summary_data': dict(combined_summary_data),
            'pgr_overall_summary': pgr_overall_summary,
            'pgtl_overall_summary': pgtl_overall_summary,
        }
    )





from.forms import OperationalUserForm
from.models import OperationalUser
def create_operational_user(request):
    if request.method == 'POST':
        form = OperationalUserForm(request.POST,request.FILES)
        if form.is_valid():           
            form.save()
            messages.success(request, "Entries created successfully")
            return redirect('common:view_operational_user')  
    else:
        form = OperationalUserForm()
    return render(request, 'common/create_operational_user.html', {'form': form})


def view_operational_user(request):
    user_list = OperationalUser.objects.all().order_by('-created_at')
    form = PGRViewForm(request.GET or None)
   
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        user_name = form.cleaned_data.get('pgr')   

        if start_date and end_date:
            user_list = user_list.filter(created_at__range=(start_date, end_date))
           
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            user_list = user_list.filter(created_at__range=(start_date, end_date))
          
        if region:
            user_list = user_list.filter(region=region)
        if zone:
            user_list = user_list.filter(zone=zone)
        if mp:
            user_list = user_list.filter(mp=mp)
   
    form = PGRViewForm()
    return render(request, 'common/view_operational_user.html',{'user_list':user_list,'form':form})



def update_operational_user(request,user_id):
    user_instance =get_object_or_404(OperationalUser, id=user_id)
    form=OperationalUserForm(request.POST, request.FILES,instance = user_instance)   
    if form.is_valid():
        form.save()
        return redirect('common:view_operational_user')  # Replace 'success_page' with the name of your success page
    else:
        form = OperationalUserForm(instance=user_instance)        
    form = OperationalUserForm(instance=user_instance) 
    return render(request, 'common/create_operational_user.html',{'form':form,'user_instance':user_instance})



def upload_pgr_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            try:
                df = pd.read_excel(excel_file)
                for _, row in df.iterrows():
                    PGRdatabase.objects.create(
                        region=row['region'],
                        zone=row['zone'],
                        mp=row['mp'],
                        name=row['name'],
                        pgr_id=row.get('pgr_id', None),
                        PGR_type=row['PGR_type'],
                        phone=row['phone'],
                        email=row['email'],
                        address=row['address'],
                        joining_date=row.get('joining_date', None),
                        reference_person_name=row.get('reference_person_name', None),
                        reference_person_phone=row.get('reference_person_phone', None),
                        # Assuming PGR_photo and PGR_birth_certificate are URLs or paths in your Excel file
                        PGR_photo=row.get('PGR_photo', None),
                        PGR_birth_certificate=row.get('PGR_birth_certificate', None)
                    )
                messages.success(request, "Data uploaded successfully")
                return redirect('tickets:view_pgr_database')
            except Exception as e:
                messages.error(request, f"Error processing file: {e}")
    else:
        form = ExcelUploadForm()
    return render(request, 'common/upload_pgr_excel.html', {'form': form})



def fuel_by_pump2(request):
    form = FuelWithdrawForm()
    pg_fuel_data = []
    vehicle_fuel_data = []
    combined_fuel_data = []
    if request.method == 'POST':
        form = FuelWithdrawForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            payments_data = fuelPumpPayment.objects.filter(payment_date__range=[start_date, end_date]) \
                                .values('pump__fuel_pump_name') \
                                .annotate(total_payment=Sum('payment_amount')) \
                                .order_by('pump__fuel_pump_name')

            pg_fuel_data = PGFuelRefill.objects.filter(refill_date__range=[start_date, end_date]) \
                            .values('fuel_pump__fuel_pump_name', 'fuel_pump__advance_amount_given') \
                            .annotate(total_fuel=Sum('refill_amount'), total_fuel_cost=Sum('fuel_cost')) \
                            .order_by('fuel_pump__fuel_pump_name')

            vehicle_fuel_data = FuelRefill.objects.filter(refill_date__range=[start_date, end_date]) \
                                .values('pump__fuel_pump_name', 'pump__advance_amount_given') \
                                .annotate(total_fuel=Sum('refill_amount'), total_fuel_cost=Sum('fuel_cost')) \
                                .order_by('pump__fuel_pump_name')
    else:
        pg_fuel_data = PGFuelRefill.objects.values('fuel_pump__fuel_pump_name', 'fuel_pump__advance_amount_given') \
                        .annotate(total_fuel=Sum('refill_amount'), total_fuel_cost=Sum('fuel_cost')) \
                        .order_by('fuel_pump__fuel_pump_name')

        vehicle_fuel_data = FuelRefill.objects.values('pump__fuel_pump_name', 'pump__advance_amount_given') \
                            .annotate(total_fuel=Sum('refill_amount'), total_fuel_cost=Sum('fuel_cost')) \
                            .order_by('pump__fuel_pump_name')

    combined_data = defaultdict(lambda: {'total_fuel': 0.0, 'total_fuel_cost': 0.0, 'advance_amount_given': 0.0, 'remaining_cost': 0.0})
    for data in pg_fuel_data:
        fuel_pump_name = data['fuel_pump__fuel_pump_name'] or 'Local purchase'
        combined_data[fuel_pump_name]['total_fuel'] += float(data['total_fuel'])
        combined_data[fuel_pump_name]['total_fuel_cost'] += float(data['total_fuel_cost'])
        advance_amount_given = float(data.get('fuel_pump__advance_amount_given', 0))
        combined_data[fuel_pump_name]['advance_amount_given'] = advance_amount_given
        combined_data[fuel_pump_name]['remaining_cost'] = combined_data[fuel_pump_name]['total_fuel_cost'] - advance_amount_given
    for data in vehicle_fuel_data:
        fuel_pump_name = data['pump__fuel_pump_name'] or 'Local purchase'
        combined_data[fuel_pump_name]['total_fuel'] += float(data['total_fuel'])
        combined_data[fuel_pump_name]['total_fuel_cost'] += float(data['total_fuel_cost'])
        advance_amount_given = float(data.get('pump__advance_amount_given', 0))
        combined_data[fuel_pump_name]['advance_amount_given'] = advance_amount_given
        combined_data[fuel_pump_name]['remaining_cost'] = advance_amount_given - combined_data[fuel_pump_name]['total_fuel_cost']

    combined_fuel_data = [{'fuel_pump_name': pump_name, 'total_fuel': data['total_fuel'], 'total_fuel_cost': data['total_fuel_cost'], 'advance_amount_given': data['advance_amount_given'], 'remaining_cost': data['remaining_cost']} for pump_name, data in combined_data.items()]
    combined_fuel_data.sort(key=lambda x: x['fuel_pump_name'])

    return render(request, 'common/fuel_withdraw_by_pump.html', {
        'form': form,
        'combined_fuel_data': combined_fuel_data,
        'pg_fuel_data': pg_fuel_data,
        'vehicle_fuel_data': vehicle_fuel_data
    })



def fuel_by_pump(request):
    form = FuelWithdrawForm()
    pg_fuel_data = []
    vehicle_fuel_data = []
    combined_fuel_data = []
    if request.method == 'POST':
        form = FuelWithdrawForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            pg_fuel_data = PGFuelRefill.objects.filter(refill_date__range=[start_date, end_date]) \
                            .values('fuel_pump__id', 'fuel_pump__fuel_pump_name', 'fuel_pump__advance_amount_given') \
                            .annotate(total_fuel=Sum('refill_amount'), total_fuel_cost=Sum('fuel_cost')) \
                            .order_by('fuel_pump__fuel_pump_name')
            vehicle_fuel_data = FuelRefill.objects.filter(refill_date__range=[start_date, end_date]) \
                                .values('pump__id', 'pump__fuel_pump_name', 'pump__advance_amount_given') \
                                .annotate(total_fuel=Sum('refill_amount'), total_fuel_cost=Sum('fuel_cost')) \
                                .order_by('pump__fuel_pump_name')
            payments_data = fuelPumpPayment.objects.filter(payment_date__range=[start_date, end_date]) \
                                .values('pump__id', 'pump__fuel_pump_name') \
                                .annotate(total_payment=Sum('payment_amount')) \
                                .order_by('pump__fuel_pump_name')
    else:
        pg_fuel_data = PGFuelRefill.objects.values('fuel_pump__id', 'fuel_pump__fuel_pump_name', 'fuel_pump__advance_amount_given') \
                        .annotate(total_fuel=Sum('refill_amount'), total_fuel_cost=Sum('fuel_cost')) \
                        .order_by('fuel_pump__fuel_pump_name')
        vehicle_fuel_data = FuelRefill.objects.values('pump__id', 'pump__fuel_pump_name', 'pump__advance_amount_given') \
                            .annotate(total_fuel=Sum('refill_amount'), total_fuel_cost=Sum('fuel_cost')) \
                            .order_by('pump__fuel_pump_name')
        payments_data = fuelPumpPayment.objects.values('pump__id', 'pump__fuel_pump_name') \
                            .annotate(total_payment=Sum('payment_amount')) \
                            .order_by('pump__fuel_pump_name')

    combined_data = defaultdict(lambda: {
        'total_fuel': 0.0,
        'total_fuel_cost': 0.0,
        'advance_amount_given': 0.0,
        'remaining_cost': 0.0,
        'total_payment': 0.0,
        'pump_id': None
    })

    for data in pg_fuel_data:
        fuel_pump_name = data['fuel_pump__fuel_pump_name'] or 'Local purchase'
        combined_data[fuel_pump_name]['total_fuel'] += float(data['total_fuel'] or 0)
        combined_data[fuel_pump_name]['total_fuel_cost'] += float(data['total_fuel_cost'] or 0)
        advance_amount_given = float(data.get('fuel_pump__advance_amount_given') or 0)
        combined_data[fuel_pump_name]['advance_amount_given'] = advance_amount_given
        combined_data[fuel_pump_name]['remaining_cost'] = advance_amount_given - combined_data[fuel_pump_name]['total_fuel_cost']
        combined_data[fuel_pump_name]['pump_id'] = data['fuel_pump__id']
    for data in vehicle_fuel_data:
        fuel_pump_name = data['pump__fuel_pump_name'] or 'Local purchase'
        combined_data[fuel_pump_name]['total_fuel'] += float(data['total_fuel'] or 0)
        combined_data[fuel_pump_name]['total_fuel_cost'] += float(data['total_fuel_cost'] or 0)
        advance_amount_given = float(data.get('pump__advance_amount_given') or 0)
        combined_data[fuel_pump_name]['advance_amount_given'] = advance_amount_given
        combined_data[fuel_pump_name]['remaining_cost'] = advance_amount_given - combined_data[fuel_pump_name]['total_fuel_cost']
        combined_data[fuel_pump_name]['pump_id'] = data['pump__id']
    for data in payments_data:
        fuel_pump_name = data['pump__fuel_pump_name'] or 'Local purchase'
        combined_data[fuel_pump_name]['total_payment'] += float(data['total_payment'] or 0)
        combined_data[fuel_pump_name]['remaining_cost'] += float(data['total_payment'] or 0)

    combined_fuel_data = [
        {
            'fuel_pump_name': pump_name,
            'total_fuel': data['total_fuel'],
            'total_fuel_cost': data['total_fuel_cost'],
            'advance_amount_given': data['advance_amount_given'],
            'remaining_cost': data['remaining_cost'],
            'total_payment': data['total_payment'],
            'pump_id': data['pump_id']
        }
        for pump_name, data in combined_data.items()
    ]
    combined_fuel_data.sort(key=lambda x: x['fuel_pump_name'])
    return render(request, 'common/fuel_withdraw_by_pump.html', {
        'form': form,
        'combined_fuel_data': combined_fuel_data,
        'pg_fuel_data': pg_fuel_data,
        'vehicle_fuel_data': vehicle_fuel_data
    })




def datewise_fuel_withdraw(request):
    pg_fuel_data = []
    vehicle_fuel_data = []
    if request.method == 'POST':
        form = FuelPumpSearchForm(request.POST)
        if form.is_valid():
            fuel_pump_name = form.cleaned_data['fuel_pump_name']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            pg_fuel_data = PGFuelRefill.objects.filter(
                fuel_pump__fuel_pump_name=fuel_pump_name,
                refill_date__range=[start_date, end_date]
            ).order_by('refill_date')
            vehicle_fuel_data = FuelRefill.objects.filter(
                pump__fuel_pump_name=fuel_pump_name,
                refill_date__range=[start_date, end_date]
            ).order_by('refill_date')

            return render(request, 'common/datewise_fuel_withdraw.html', {
                'form': form,
                'pg_fuel_data': pg_fuel_data,
                'vehicle_fuel_data': vehicle_fuel_data,
                'fuel_pump_name': fuel_pump_name,
            })
    else:
        form = FuelPumpSearchForm()
    return render(request, 'common/datewise_fuel_withdraw.html', {'form': form})


def fuel_pump_payment(request):
    if request.method == 'POST':
        form = FuelPumpPaymentForm(request.POST)
        if form.is_valid():          
            payment_data = form.save(commit=False)
            payment_data.payment_id = generate_unique_finance_requisition_number()
            payment_data.save()
            return redirect('common:fuel_by_pump')
        else:
            form = FuelPumpPaymentForm()
    form=FuelPumpPaymentForm()
    return render(request, 'common/fuel_pump_payment.html',{'form':form})



def view_pump_payment_history(request, pump_id):
    start_date=None
    end_date =None
    pump = get_object_or_404(FuelPumpDatabase, id=pump_id)
    pump_payment_data = fuelPumpPayment.objects.filter(pump=pump)
    form=PGRViewForm(request.GET)
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        if start_date and end_date:
             pump_payment_data = pump_payment_data.filter(payment_date__range=[start_date, end_date]) \

    form=PGRViewForm(request.GET)
    return render(request, 'common/view_fuel_pump_payment.html', {
        'pump': pump,
        'pump_payment_data': pump_payment_data,
        'form':form
    })


def all_expenditure(request):
    adhoc_vehicle_expense = AdhocVehicleAttendance.objects.all()
    adhoc_man_expense = AdhocAttendance.objects.all()
    daily_expense = DailyExpenseRequisition.objects.all()
    civil_power_expense = CivilPower.objects.all()
    tickets = eTicket.objects.all()
    money_requisitions = MoneyRequisition.objects.all()
    start_date = None
    end_date = None
    days = None
    region = None
    zone = None
    mp = None
    form = AllExpenseForm(request.GET or None)
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        if start_date and end_date:
            date_range = (start_date, end_date)
            adhoc_vehicle_expense = adhoc_vehicle_expense.filter(created_at__range=date_range)
            adhoc_man_expense = adhoc_man_expense.filter(created_at__range=date_range)
            daily_expense = daily_expense.filter(created_at__range=date_range)
            civil_power_expense = civil_power_expense.filter(created_at__range=date_range)
            tickets = tickets.filter(created_at__range=date_range)
            money_requisitions = money_requisitions.filter(created_at__range=date_range)
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            date_range = (start_date, end_date)
            adhoc_vehicle_expense = adhoc_vehicle_expense.filter(created_at__range=date_range)
            adhoc_man_expense = adhoc_man_expense.filter(created_at__range=date_range)
            daily_expense = daily_expense.filter(created_at__range=date_range)
            civil_power_expense = civil_power_expense.filter(created_at__range=date_range)
            tickets = tickets.filter(created_at__range=date_range)
            money_requisitions = money_requisitions.filter(created_at__range=date_range)
        if region:
            adhoc_vehicle_expense = adhoc_vehicle_expense.filter(vehicle__region=region)
            adhoc_man_expense = adhoc_man_expense.filter(pgr__region=region)
            daily_expense = daily_expense.filter(region=region)
            civil_power_expense = civil_power_expense.filter(region=region)
            tickets = tickets.filter(region=region)
            money_requisitions = money_requisitions.filter(region=region)
        if zone:
            adhoc_vehicle_expense = adhoc_vehicle_expense.filter(vehicle__zone=zone)
            adhoc_man_expense = adhoc_man_expense.filter(pgr__zone=zone)
            daily_expense = daily_expense.filter(zone=zone)
            civil_power_expense = civil_power_expense.filter(zone=zone)
            tickets = tickets.filter(zone=zone)
            money_requisitions = money_requisitions.filter(zone=zone)

    adhoc_vehicle_expense = adhoc_vehicle_expense.values('vehicle__region', 'vehicle__zone').annotate(
        total_adhoc_vehicle=Sum(F('adhoc_vehicle_total_bill_amount'))
    )
    adhoc_man_expense = adhoc_man_expense.values('pgr__region', 'pgr__zone').annotate(
        total_adhoc_man=Sum(F('adhoc_bill_amount'))
    )
    daily_expense = daily_expense.values('region', 'zone').annotate(
        total_daily=Sum(F('requisition_amount')),
        total_daily_CM_work=Sum(F('requisition_amount'),filter=Q(work_type = 'CM_work')),
        total_daily_PM_work=Sum(F('requisition_amount'), filter=Q(work_type = 'PM_work')),
        total_daily_disaster=Sum(F('requisition_amount'),filter=Q(work_type ='disaster')),
        total_daily_Civil_power=Sum(F('requisition_amount'),filter=Q(work_type ='Civil_power')),
    )


   
    tickets = tickets.values('region', 'zone').annotate(
        total_TT=Count(F('internal_ticket_number')),      
        total_PGRH = ExpressionWrapper(
            Sum(F('internal_generator_running_hours')) / timedelta(hours=1),
            output_field=DecimalField(max_digits=10,decimal_places=2)
        )
    )
    money_requisitions = money_requisitions.values('region', 'zone').annotate(
        total_approved_amount=Sum(F('approved_amount'), filter=Q(purpose='Operations')),
        total_approved_amount_operation=Sum(F('approved_amount'), filter=Q(purpose='Operations')),
        total_approved_amount_adhoc_man=Sum(F('approved_amount'), filter=Q(purpose='Adhoc_man')),
        total_approved_amount_adhoc_vehicle=Sum(F('approved_amount'), filter=Q(purpose='Adhoc_vehicle')),        
        total_approved_amount_Civil_power=Sum(F('approved_amount'), filter=Q(purpose='Civil_power')),
        total_approved_amount_disaster=Sum(F('approved_amount'), filter=Q(purpose='disaster')),
    )

    summary_dict = {}
    def get_summary_dict_template():
        return {
            'total_adhoc_vehicle': 0,
            'total_adhoc_man': 0,


            'total_daily_CM_work': 0,
            'total_daily_PM_work': 0,
            'total_daily_Civil_power': 0,
            'total_daily_disaster': 0,
            'sub_total_operational_cost':0,


            'total_civil_power': 0,
            'total_TT': 0,
            'total_PGRH': 0,
            'total_approved_amount': 0,

            'total_approved_amount_operation': 0,
            'total_approved_amount_adhoc_man': 0,
            'total_approved_amount_adhoc_vehicle': 0,
            'total_approved_amount_Civil_power': 0,
            'total_approved_amount_disaster': 0,

            'total_expense':0,
            'total_approved':0
          

            
        }

    for item in adhoc_vehicle_expense:
        key = (item['vehicle__region'], item['vehicle__zone'])
        summary_dict.setdefault(key, get_summary_dict_template())
        summary_dict[key]['total_adhoc_vehicle'] = item['total_adhoc_vehicle'] or 0

    for item in adhoc_man_expense:
        key = (item['pgr__region'], item['pgr__zone'])
        summary_dict.setdefault(key, get_summary_dict_template())
        summary_dict[key]['total_adhoc_man'] = item['total_adhoc_man'] or 0

    for item in daily_expense:
        key = (item['region'], item['zone'])
        summary_dict.setdefault(key, get_summary_dict_template())  
        summary_dict[key]['total_daily_CM_work'] = item['total_daily_CM_work'] or 0
        summary_dict[key]['total_daily_PM_work'] = item['total_daily_PM_work'] or 0
        summary_dict[key]['total_daily_Civil_power'] = item['total_daily_Civil_power'] or 0
        summary_dict[key]['total_daily_disaster'] = item['total_daily_disaster'] or 0
  
    for item in tickets:
        key = (item['region'], item['zone'])
        summary_dict.setdefault(key, get_summary_dict_template())
        summary_dict[key]['total_TT'] = item['total_TT'] or 0
        summary_dict[key]['total_PGRH'] = item['total_PGRH'] or 0
    for item in money_requisitions:
        key = (item['region'], item['zone'])
        summary_dict.setdefault(key, get_summary_dict_template())      
        summary_dict[key]['total_approved_amount_operation'] = item['total_approved_amount_operation'] or 0
        summary_dict[key]['total_approved_amount_adhoc_man'] = item['total_approved_amount_adhoc_man'] or 0
        summary_dict[key]['total_approved_amount_adhoc_vehicle'] = item['total_approved_amount_adhoc_vehicle'] or 0        
        summary_dict[key]['total_approved_amount_Civil_power'] = item['total_approved_amount_Civil_power'] or 0
        summary_dict[key]['total_approved_amount_disaster'] = item['total_approved_amount_disaster'] or 0


    total_expense = 0
    total_approved = 0
    cash_in_hand = 0
    for key, value in summary_dict.items():
        value['sub_total_operational_cost'] = value['total_daily_CM_work'] + value['total_daily_PM_work'] + value['total_daily_disaster'] 

        value['total_expense'] = value['total_adhoc_vehicle'] + value['total_adhoc_man'] + value['sub_total_operational_cost'] + value['total_daily_Civil_power']
        value['total_approved'] = value['total_approved_amount_operation'] + value['total_approved_amount_adhoc_man'] + value['total_approved_amount_adhoc_vehicle'] + value['total_approved_amount_Civil_power']
        value['cash_in_hand'] = value['total_approved'] - value['total_expense']
        total_expense += value['total_expense']
        total_approved += value['total_approved']
        cash_in_hand += value['cash_in_hand']

    context = {
        'form': form,
        'summary_dict': summary_dict,
        'total_expense': total_expense,
        'total_approved': total_approved,
        'days': days,
        'start_date': start_date,
        'end_date': end_date
    }
    
    form = AllExpenseForm()
    return render(request, 'common/all_expenses_summary.html', context)




def operational_resource_management(request):
    return render(request,'common/operational_resource_management.html') # for operational resource dashboard shortcut

