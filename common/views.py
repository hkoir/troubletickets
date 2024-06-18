from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import FuelPumpDatabaseForm
from tickets .views import generate_unique_finance_requisition_number
from django.shortcuts import render, redirect,get_object_or_404
from django.db.models import Sum, Avg,Count,Q,Case, When, IntegerField,F,Max,DurationField, DecimalField
import random,json,uuid,base64,csv


from django.shortcuts import render
from django.db.models import Count
from .models import PGRdatabase

from.forms import ExcelUploadForm
import pandas as pd
from.forms import PGRForm
from tickets.views import generate_unique_ticket_number

from datetime import datetime,timedelta
from.forms import PGRViewForm

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
            return redirect('common:create_fuel_pump_database')
    else:
        form = FuelPumpDatabaseForm()

    return render(request, 'common/create_fuel_pump.html', {'form': form})



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



def view_pgr_database(request):    
    form = PGRViewForm(request.GET or {'days': 20})
    pgr_list = PGRdatabase.objects.all().order_by('-created_at')
    
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        
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

    else:
        form = PGRViewForm()
    form = PGRViewForm()
    return render(request,'common/view_pgr_database.html',
        {
        'pgr_list':pgr_list,
        'form':form,
        'days':days,
        'start_date':start_date,
        'end_date':end_date
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



def pgr_summary_view(request):   
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




def operational_resource_management(request):
    return render(request,'common/operational_resource_management.html') # for operational resource dashboard shortcut

