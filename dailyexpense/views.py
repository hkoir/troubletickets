import xlsxwriter,csv,random,calendar
from itertools import groupby
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,JsonResponse
from django.http import HttpResponseBadRequest
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal
from django.shortcuts import render, redirect,get_object_or_404
from django.db.models import Sum, Avg,Count,Q,Case, When, IntegerField,F,Max,DurationField, DecimalField,FloatField
from django.db.models import Value,ExpressionWrapper

from .forms import ExpenseRequisitionForm,SummaryExpensesForm,ExpenseRequisitionStatusForm,MoneyRequisitionForm
from .models import MoneyRequisition,SummaryExpenses,DailyExpenseRequisition,AdhocRequisition
from .forms import ZoneWiseExpensesForm,AdhocRequisitionStatusForm,AdhocRequisitionForm,dailyExpenseSummaryForm
from.forms import MoneySendingForm

from common.models import FuelPumpDatabase,PGTLdatabase
from tickets.forms import SummaryReportChartForm
from tickets.models import eTicket,PGRdatabase
from tickets.views import generate_unique_finance_requisition_number
from vehicle.models import AddVehicleInfo
from generator.models import AddPGInfo

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from vehicle.models import AdhocVehicleRequisition
from adhocman.models import AdhocManRequisition
from collections import defaultdict



def expense_advance_management(request):
    return render(request,'expenses/expense_advance_management.html')# for expense and advance management dashboard shortcut

def common_search(request):
    query = request.GET.get('q', '').strip().lower()
    results = []

    if query:
        eticket_results = eTicket.objects.filter(
            Q(region__icontains=query) |
            Q(zone__icontains=query) |
            Q(mp__icontains=query) |
            Q(internal_ticket_number__icontains=query)
        ).values('id', 'region', 'zone', 'mp', 'internal_ticket_number')
        for et in eticket_results:
            results.extend([
                {'id': et['id'], 'text': et['region'], 'model': 'eTicket'},
                {'id': et['id'], 'text': et['zone'], 'model': 'eTicket'},
                {'id': et['id'], 'text': et['mp'], 'model': 'eTicket'},
                {'id': et['id'], 'text': et['internal_ticket_number'], 'model': 'eTicket'}
            ])

        addpginfo_results = AddPGInfo.objects.filter(
            Q(PGNumber__icontains=query) |
            Q(PG_brand__icontains=query)
        ).values('id', 'PGNumber', 'PG_brand')

        for pg in addpginfo_results:
            results.extend([
                {'id': pg['id'], 'text': pg['PGNumber'], 'model': 'AddPGInfo'},
                {'id': pg['id'], 'text': pg['PG_brand'], 'model': 'AddPGInfo'}
            ])
        addvehicleinfo_results = AddVehicleInfo.objects.filter(
            Q(vehicle_reg_number__icontains=query) |
            Q(vehicle_brand_name__icontains=query)
        ).values('id', 'vehicle_reg_number', 'vehicle_brand_name')

        for vh in addvehicleinfo_results:
            results.extend([
                {'id': vh['id'], 'text': vh['vehicle_reg_number'], 'model': 'AddVehicleInfo'},
                {'id': vh['id'], 'text': vh['vehicle_brand_name'], 'model': 'AddVehicleInfo'}
            ])

        addpumpInfo_results = FuelPumpDatabase.objects.filter(
            Q(fuel_pump_name__icontains=query) |
            Q(fuel_pump_company_name__icontains=query)
        ).values('id', 'fuel_pump_name', 'fuel_pump_company_name')

        for pump in addpumpInfo_results:
            results.extend([
                {'id': pump['id'], 'text': pump['fuel_pump_name'], 'model': 'FuelPumpDatabase'},
                {'id': pump['id'], 'text': pump['fuel_pump_company_name'], 'model': 'FuelPumpDatabase'}
            ])

        pgr_results = PGRdatabase.objects.filter(
            Q(name__icontains=query)
        ).values('id', 'name')
        for pgr in pgr_results:
            results.append({'id': pgr['id'], 'text': pgr['name'], 'model': 'PGRdatabase'})
        pgtl_results = PGTLdatabase.objects.filter(
            Q(name__icontains=query)
        ).values('id', 'name')
        for pgtl in pgtl_results:
            results.append({'id': pgtl['id'], 'text': pgtl['name'], 'model': 'PGTLdatabase'})
        vehicle_requisition_results = AdhocVehicleRequisition.objects.filter(
            Q(requisition_id__icontains=query)
        ).values('id', 'requisition_id')
        for req in vehicle_requisition_results:
            results.append({'id': req['id'], 'text': req['requisition_id'], 'model': 'AdhocVehicleRequisition'})
        man_requisition_results = AdhocManRequisition.objects.filter(
            Q(requisition_id__icontains=query)
        ).values('id', 'requisition_id')
        for req in man_requisition_results:          
            results.append({'id': req['id'], 'text': req['requisition_id'], 'model': 'AdhocManRequisition'})
   
    return JsonResponse({'results': results})





################## management approval for money requisition ##################################

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



@manager_level_required('first_level')
@login_required
def money_requisition(request):
    if request.method == 'POST':   
        form = MoneyRequisitionForm(request.POST, request.FILES)
        if form.is_valid():        
            form.instance.requester = request.user
            form.instance.requisition_number = generate_unique_finance_requisition_number()
            form.save()
            return redirect('dailyexpense:all_approval_status')
    else:     
        form = MoneyRequisitionForm()
    return render(request, 'expenses/money_requisition/money_requisition_form.html', {'form': form})


@login_required
def all_approval_status(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    region_approvals = None
    zone_approvals = None
    form = ExpenseRequisitionStatusForm(request.GET or {'days': 20})
    money_requisitions = MoneyRequisition.objects.all().order_by('-created_at')
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        purpose_approvals = defaultdict(list)
        if start_date and end_date:
            money_requisitions = money_requisitions.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            money_requisitions = money_requisitions.filter(created_at__range=(start_date, end_date))

        if region:
            money_requisitions = money_requisitions.filter(region=region)
        if zone:
            money_requisitions = money_requisitions.filter(zone=zone)      
        region_approvals = money_requisitions.values('region').annotate(
            total_requisition=Sum('requisition_amount'),
            total_approved=Sum('approved_amount'),
            total_approved_adhoc_vehicle=Sum(
                    Case(
                        When(purpose='Adhoc_vehicle', then='approved_amount'),
                        default=Value(0),
                        output_field=DecimalField() 
                    )
                ),
            total_approved_adhoc_man=Sum(
                    Case(
                        When(purpose='Adhoc_man', then='approved_amount'),
                        default=Value(0),
                        output_field=DecimalField() 
                    )
                ),

            total_approved_operations=Sum(
                    Case(
                        When(purpose='Operations', then='approved_amount'),
                        default=Value(0),
                        output_field=DecimalField() 
                    )
                ),
            num_requisitions=Count('id')
        ).order_by('region')

        zone_approvals = money_requisitions.values('zone').annotate(
            total_requisition=Sum('requisition_amount'),
            total_approved=Sum('approved_amount'),

             total_approved_adhoc_vehicle=Sum(
                    Case(
                        When(purpose='Adhoc_vehicle', then='approved_amount'),
                        default=Value(0),
                        output_field=DecimalField() 
                    )
                ),
            total_approved_adhoc_man=Sum(
                    Case(
                        When(purpose='Adhoc_man', then='approved_amount'),
                        default=Value(0),
                        output_field=DecimalField() 
                    )
                ),

            total_approved_operations=Sum(
                    Case(
                        When(purpose='Operations', then='approved_amount'),
                        default=Value(0),
                        output_field=DecimalField() 
                    )
                ),
            num_requisitions=Count('id')
        ).order_by('zone')


        purpose_approvals = {}
        purposes = money_requisitions.values_list('purpose', flat=True).distinct()
        for purpose in purposes:
            approvals = money_requisitions.filter(purpose=purpose).values('region', 'zone').annotate(
                total_requisition=Sum('requisition_amount'),
                total_approved=Sum('approved_amount'),
                num_requisitions=Count('id')
            ).order_by('region', 'zone')
            purpose_approvals[purpose] = approvals
    page_obj = None
    money_per_page = 5
    paginator = Paginator(money_requisitions, money_per_page)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)    
    form = ExpenseRequisitionStatusForm()
    return render(request, 'expenses/money_requisition/approval_history.html', {
        'money_requisitions':money_requisitions,
        'page_obj': page_obj,
        'region_approvals': region_approvals,
        'zone_approvals': zone_approvals,
        'purpose_approvals': purpose_approvals,
        'days': days,
        'form': form,
        'start_date': start_date,
        'end_date': end_date
    })



@login_required
def requisition_approval(request, requisition_id):
    requisition = get_object_or_404(MoneyRequisition, id=requisition_id)
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
            approved_amount = request.POST.get('approved_amount')
            approval_date = timezone.now() 
            try:
                approved_amount = Decimal(approved_amount)
            except ValueError:
                 messages.error(request, "Invalid approved amount")
                 return redirect('dailyexpense:requisition_approval', requisition_id=requisition_id)                      
            requisition.approved_amount = approved_amount            
            if required_level == 'first_level':
                requisition.level1_comments = comments
                requisition.level1_approval_status = approval_status
                requisition.level1_approval_date =  approval_date
            elif required_level == 'second_level':
                requisition.level2_comments = comments
                requisition.level2_approval_status = approval_status
                requisition.level2_approval_date =  approval_date
            elif required_level == 'third_level':
                requisition.level3_comments = comments
                requisition.level3_approval_status = approval_status
                requisition.level3_approval_date = approval_date         
            requisition.save()
            return redirect('dailyexpense:all_approval_status')
        else:
            return render(request, 'expenses/money_requisition/money_approval_form.html', {'requisition': requisition})
    else:        
        messages.error(request, "You can not get access at this moment. May be due to previous level approval is pending or you are not authorized from your management")
        return redirect('dailyexpense:all_approval_status')




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
def download_money_requisition_data(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="money_requisition_data.xlsx"'
    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet()    
    headers = ['Date','Requisition Number','Reqquester', 'Region', 'Zone','Purpose', 'Requisition Amount','Approved Amount', 'Level 1 Approval', 
               'Level 1 Approval Date', 'Level 2 Approval', 'Level 2 Approval Date', 'Level 3 Approval', 
               'Level 3 Approval Date', 'Receiving Status']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)  
    requisitions = MoneyRequisition.objects.all()
    for row, requisition in enumerate(requisitions, start=1):
        update_at_str = timezone.localtime(requisition.update_at).strftime('%Y-%m-%d %H:%M:%S')
        worksheet.write(row, 0, str(update_at_str))
        worksheet.write(row, 1, str(requisition.requisition_number))      
        worksheet.write(row, 2, str(requisition.requester))
        worksheet.write(row, 3, str(requisition.region))
        worksheet.write(row, 4, str(requisition.zone))
   
        worksheet.write(row, 5, requisition.purpose)
        worksheet.write(row, 6, float(requisition.requisition_amount))
        worksheet.write(row, 7, float(requisition.approved_amount))
        worksheet.write(row, 8, requisition.level1_approver)
        worksheet.write(row, 9, str(requisition.level1_approval_date))
        worksheet.write(row, 10, requisition.level2_approver)
        worksheet.write(row, 11, str(requisition.level2_approval_date))
        worksheet.write(row, 12, requisition.level3_approver)
        worksheet.write(row, 13, str(requisition.level3_approval_date))
        worksheet.write(row, 14, requisition.receiving_status)

    workbook.close()
    return response



@login_required
def update_money_requisition(request,requisition_id):
    requisition = get_object_or_404(MoneyRequisition, id=requisition_id)
    if request.method == 'POST':
        form = MoneySendingForm(request.POST, request.FILES)
        if form.is_valid():        
            if form.cleaned_data['UploadPicture'] and form.cleaned_data['TakePicture']:
                print('Please select only one option for picture')
                form.add_error('UploadPicture', 'Please select only one option for picture')
                form.add_error('TakePicture', 'Please select only one option for picture')
            elif form.cleaned_data['UploadPicture']:
                requisition.sending_document = form.cleaned_data['UploadPicture']
            elif form.cleaned_data['TakePicture']:
                requisition.sending = form.cleaned_data['TakePicture']           
            requisition.save()
            return redirect('dailyexpense:all_approval_status')
    else:     
        form = MoneySendingForm()
    return render(request, 'expenses/money_requisition/money_requisition_form.html', {'form': form})



@login_required
def mark_received(request, requisition_id): 
    requisition = get_object_or_404(MoneyRequisition, id=requisition_id)   
    if requisition.requester == request.user:      
        requisition.receiving_status = 'Received'
        requisition.save()
        messages.success(request, 'Requisition marked as received successfully.')
    else:
        messages.error(request, 'You are not authorized to mark this requisition as received.')
    return redirect('dailyexpense:all_approval_status')


############################## Daily expenses for field force #################################################

@login_required
def create_expense_requisition(request):
    if request.method == 'POST':   
        form = ExpenseRequisitionForm(request.POST, request.FILES)
        if form.is_valid():        
            form.instance.expense_requester = request.user
            form.instance.expense_requisition_number = generate_unique_finance_requisition_number()
            form.save()
            return redirect('dailyexpense:expense_approval_status')
    else:     
        form = ExpenseRequisitionForm()
    return render(request, 'expenses/daily_expenses/create_expense_requisition.html', {'form': form})


@login_required
def expense_approval_status(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None
    form = ExpenseRequisitionStatusForm(request.GET or {'days': 20})
    expense_requisitions =  DailyExpenseRequisition.objects.all().order_by('-created_at')
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        if start_date and end_date:
            expense_requisitions = expense_requisitions.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            expense_requisitions = expense_requisitions.filter(created_at__range=(start_date, end_date))
        if region:
            expense_requisitions = expense_requisitions.filter(region=region)
        if zone:
           expense_requisitions = expense_requisitions.filter(zone=zone)
        if mp:
            expense_requisitions =  expense_requisitions.filter(mp=mp)
        region_approvals = expense_requisitions.values('region').annotate(
            total_requisition=Sum('requisition_amount'),
            total_approved=Sum('approved_amount'),
            num_requisitions=Count('id')
        ).order_by('region')
        zone_approvals = expense_requisitions.values('zone').annotate(
            total_requisition=Sum('requisition_amount'),
            total_approved=Sum('approved_amount'),
            num_requisitions=Count('id')
        ).order_by('zone')
    page_obj = None
    money_per_page = 2
    paginator = Paginator(expense_requisitions, money_per_page)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    form = ExpenseRequisitionStatusForm()
    return render(request, 'expenses/daily_expenses/expense_approval_status.html', {
        'expense_requisitions':expense_requisitions,
        'page_obj': page_obj,
        'region_approvals': region_approvals,
        'zone_approvals': zone_approvals,
        'days': days,
        'form': form,
        'start_date': start_date,
        'end_date': end_date
    })



@login_required
def expense_requisition_approval(request, expense_requisition_id):
    expense_requisitions = get_object_or_404(DailyExpenseRequisition, id=expense_requisition_id)
    manager_level = request.user.manager_level    
    if expense_requisitions.level1_approval_status == 'PENDING':
        required_level = 'first_level'
    elif expense_requisitions.level2_approval_status == 'PENDING':
        required_level = 'second_level'
    elif expense_requisitions.level3_approval_status == 'PENDING':
        required_level = 'third_level'
    else:  
        return JsonResponse({"message": "Requisition already approved by all levels"}, status=400)
    if manager_level == required_level:
        if request.method == 'POST':
            approval_status = request.POST.get('approval_status')
            comments = request.POST.get('comments')
            approved_amount = request.POST.get('approved_amount')
            approval_date = timezone.now() 
            try:
                approved_amount = Decimal(approved_amount)
            except ValueError:
                 messages.error(request, "Invalid approved amount")
                 return redirect('dailyexpense:expense_approval_status', expense_requisition_id=expense_requisition_id)                       
            expense_requisitions.approved_amount = approved_amount            
            if required_level == 'first_level':
                expense_requisitions.level1_comments = comments
                expense_requisitions.level1_approval_status = approval_status
                expense_requisitions.level1_approval_date =  approval_date
            elif required_level == 'second_level':
                expense_requisitions.level2_comments = comments
                expense_requisitions.level2_approval_status = approval_status
                expense_requisitions.level2_approval_date =  approval_date

            elif required_level == 'third_level':
                expense_requisitions.level3_comments = comments
                expense_requisitions.level3_approval_status = approval_status
                expense_requisitions.level3_approval_date = approval_date         
            expense_requisitions.save()
            return redirect('dailyexpense:expense_approval_status')
        else:
            return render(request, 'expenses/daily_expenses/expense_approval.html', {'expense_requisitions': expense_requisitions})
    else:        
        messages.error(request, "You can not get access at this moment. May be due to previous level approval is pending or you are not authorized from your management")
        return redirect('dailyexpense:expense_approval_status')



@login_required
def expense_received_mark(request, requisition_id): 
    requisition = get_object_or_404(DailyExpenseRequisition, id=requisition_id)   
    if (requisition.level1_approval_status == 'Approved' and 
        requisition.level2_approval_status == 'Approved' and 
        requisition.level3_approval_status == 'Approved'):        
        if requisition.expense_requester == request.user:      
            requisition.receiving_status = 'Received'
            requisition.save()
            messages.success(request, 'Requisition marked as received successfully.')
        else:
            messages.error(request, 'You are not authorized to mark this requisition as received.')
    else:
        messages.error(request, 'Cannot mark as received until all three levels approve.')
    return redirect('dailyexpense:expense_approval_status')



@login_required
def download_expense_requisition_data(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="money_requisition_data.xlsx"'
    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet()    
    headers = ['Date','Requisition Number','Requester', 'Region', 'Zone','MP','Purpose', 'Requisition Amount','Approved Amount', 'Level 1 Approval', 
               'Level 1 Approval Date', 'Level 2 Approval', 'Level 2 Approval Date', 'Level 3 Approval', 
               'Level 3 Approval Date', 'Receiving Status']    
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)  
    requisitions = DailyExpenseRequisition.objects.all()
    for row, requisition in enumerate(requisitions, start=1):
        created_at_str = timezone.localtime(requisition.created_at).strftime('%Y-%m-%d %H:%M:%S')      
        worksheet.write(row, 0, str(created_at_str))
        worksheet.write(row, 1, str(requisition.expense_requisition_number))      
        worksheet.write(row, 2, str(requisition.expense_requester))
        worksheet.write(row, 3, str(requisition.region.name))  
        worksheet.write(row, 4, str(requisition.zone.name))   
        worksheet.write(row, 5, str(requisition.mp.name))     
        worksheet.write(row, 6, str(requisition.purpose))
        worksheet.write(row, 7, float(requisition.requisition_amount))
        if requisition.approved_amount is not None:
            worksheet.write(row, 8, float(requisition.approved_amount))
        else:
            worksheet.write(row, 8, "Not Approved yet")     
        worksheet.write(row, 9, str(requisition.level1_approver))
        worksheet.write(row, 10, str(requisition.level1_approval_date))
        worksheet.write(row, 11, str(requisition.level2_approver))
        worksheet.write(row, 12, str(requisition.level2_approval_date))
        worksheet.write(row, 13, str(requisition.level3_approver))
        worksheet.write(row, 14, str(requisition.level3_approval_date))
        worksheet.write(row, 15, str(requisition.receiving_status))
    workbook.close()
    return response



def daily_expense_summary(request):
    form = dailyExpenseSummaryForm(request.GET or {'days': 7})
    grouped_summary_data = []
    start_date = None
    end_date = None
    days = None
    grouped_data=[]
    total_requisition_amount_count =None
    total_approved_amount_count =None
    local_conveyance_amount=None
    pg_carrying_cost_amount =None
    toll_amount=None
    night_bill_amount=None
    food_amount=None
    pg_local_fuel_purchase = None
    vehicle_local_fuel_purchase =None 
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        data = None    
        if start_date and end_date:
            data = DailyExpenseRequisition.objects.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            data = DailyExpenseRequisition.objects.filter(created_at__range=(start_date, end_date))
        if data is not None:
            if region:
                data = data.filter(region=region)
            if zone:
                data = data.filter(zone=zone)
            if mp:
                data = data.filter(mp=mp)

    ### aggregate as a whole expenditure ################################################
            data_grand = data.aggregate(
            total_requisition_amount=Sum('requisition_amount'),
            total_approved_amount=Sum('approved_amount'), 
             pg_local_fuel_purchase=Sum(
                    Case(
                        When(purpose='pg_local_fuel_purchase', then=F('requisition_amount')),
                        default=0,
                        output_field=FloatField()
                    )
                ),

                 vehicle_local_fuel_purchase=Sum(
                    Case(
                        When(purpose='vehicle_local_fuel_purchase', then=F('requisition_amount')),
                        default=0,
                        output_field=FloatField()
                    )
                ),          
            local_conveyance_amount=Sum(
                Case(
                    When(purpose='local_conveyance', then=F('requisition_amount')),
                    default=0,
                    output_field=FloatField()
                        )
                    ),
            pg_carrying_cost_amount=Sum(
                Case(
                    When(purpose='pg_carrying_cost', then=F('requisition_amount')),
                    default=0,
                    output_field=FloatField()
                        )
                    ),
            toll_amount=Sum(
                Case(
                    When(purpose='toll', then=F('requisition_amount')),
                    default=0,
                    output_field=FloatField()
                        )
                    ),
            food_amount=Sum(
                Case(
                    When(purpose='food', then=F('requisition_amount')),
                    default=0,
                    output_field=FloatField()
                        )
                    ),

            night_bill_amount=Sum(
                Case(
                    When(purpose='night_bill', then=F('requisition_amount')),
                    default=0,
                    output_field=FloatField()
                        )
                    ),


                  )

            total_requisition_amount_count = data_grand.get('total_requisition_amount', 0)
            total_approved_amount_count = data_grand.get('total_approved_amount', 0)
            local_conveyance_amount = data_grand.get('local_conveyance_amount', 0)
            pg_local_fuel_purchase = data_grand.get('pg_local_fuel_purchase', 0),
            vehicle_local_fuel_purchase = data_grand.get('vehicle_local_fuel_purchase', 0),
            pg_carrying_cost_amount = data_grand.get('pg_carrying_cost_amount', 0)
            toll_amount = data_grand.get('toll_amount', 0)
            night_bill_amount = data_grand.get('night_bill_amount', 0)
            food_amount = data_grand.get('food_amount', 0)

     ###### annotate for individual cost item as per region zone #################

            grouped_data = data.values('region', 'zone').annotate(
                total_requisition_amount=Sum('requisition_amount'),
                total_approved_amount=Sum('approved_amount'),

                pg_local_fuel_purchase=Sum(
                    Case(
                        When(purpose='pg_local_fuel_purchase', then=F('requisition_amount')),
                        default=0,
                        output_field=FloatField()
                    )
                ),

                 vehicle_local_fuel_purchase=Sum(
                    Case(
                        When(purpose='vehicle_local_fuel_purchase', then=F('requisition_amount')),
                        default=0,
                        output_field=FloatField()
                    )
                ),
                local_conveyance_amount=Sum(
                    Case(
                        When(purpose='local_conveyance', then=F('requisition_amount')),
                        default=0,
                        output_field=FloatField()
                    )
                ),
                pg_carrying_cost_amount=Sum(
                    Case(
                        When(purpose='pg_carrying_cost', then=F('requisition_amount')),
                        default=0,
                        output_field=FloatField()
                    )
                ),
                toll_amount=Sum(
                    Case(
                        When(purpose='toll', then=F('requisition_amount')),
                        default=0,
                        output_field=FloatField()
                    )
                ),
                food_amount=Sum(
                    Case(
                        When(purpose='food', then=F('requisition_amount')),
                        default=0,
                        output_field=FloatField()
                    )
                ),
                night_bill_amount=Sum(
                    Case(
                        When(purpose='night_bill', then=F('requisition_amount')),
                        default=0,
                        output_field=FloatField()
                    )
                )
            )

        for entry in grouped_data:
            grouped_summary_data.append({
                'region': entry['region'],
                'zone': entry['zone'],       
                'total_requisition_amount': entry.get('total_requisition_amount', 0),
                'total_approved_amount': entry.get('total_approved_amount', 0),
                'pg_local_fuel_purchase': entry.get('pg_local_fuel_purchase', 0),
                'vehicle_local_fuel_purchase': entry.get('vehicle_local_fuel_purchase', 0),
                'local_conveyance_amount': entry.get('local_conveyance_amount', 0),
                'pg_carrying_cost_amount': entry.get('pg_carrying_cost_amount', 0),
                'toll_amount': entry.get('toll_amount', 0),
                'food_amount': entry.get('food_amount', 0),
                'night_bill_amount': entry.get('night_bill_amount', 0)
            })

    form = dailyExpenseSummaryForm()
    return render(request, 'expenses/daily_expenses/daily_expense_summary.html', {
        'form': form,
        'days': days,
        'start_date':start_date,
        'end_date':end_date,     
        'grouped_summary_data': grouped_summary_data,
        'total_requisition_amount_count': total_requisition_amount_count,
        'total_approved_amount_count': total_approved_amount_count,
        'pg_local_fuel_purchase': pg_local_fuel_purchase,
        'vehicle_local_fuel_purchase': vehicle_local_fuel_purchase,
        'local_conveyance_amount': local_conveyance_amount,
        'pg_carrying_cost_amount': pg_carrying_cost_amount,
         'toll_amount':toll_amount,
         'night_bill_amount':night_bill_amount,
         'food_amount':food_amount,
    })


############################### Summary OPTIMA #######################

@login_required
def summary_expenses_form_view(request):
    if request.method == 'POST':
        form = SummaryExpensesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dailyexpense:zone_wise_expenses_view')  
    else:
        form = SummaryExpensesForm()    
    return render(request, 'expenses/grand_summary_expenses/summary_expenses_form.html', {'form': form})



@login_required
def zone_wise_expenses_view(request):
    region_zone_data = SummaryExpenses.objects.all() \
    .values('id','region', 'zone','created_at','updated_at').annotate(
        total_balance_from_previous_month=Sum('balance_from_previous_month'),
        total_amount_received=Sum('total_amount_received'),
        total_this_month_cash=Sum('this_month_cash'),
        total_office_expenses=Sum('office_expenses'),
        total_local_expenses=Sum('local_expenses'),
        total_on_demand_vehicle_cost=Sum('on_demand_vehicle_cost'),
        total_on_demand_PGR_cost=Sum('adhoc_PGR_cost'),
        total_dgow_vehicle_cost=Sum('dgow_vehicle_cost'),
        total_dgow_run_fuel_cost_cash=Sum('dgow_run_fuel_cost_cash'),
        total_pm_vehicle_fuel_cost=Sum('pm_vehicle_fuel_cost_cash'),
        total_cm_vehicle_fuel_cost=Sum('cm_vehicle_fuel_cost_cash'),
        total_pgrun_fuel_cost_cash=Sum('pgrun_fuel_cost_cash'),
        total_pgrun_fuel_cost_pump=Sum('pgrun_fuel_cost_pump'),
        total_site_pm_cost=Sum('site_pm_cost'),
        total_optima_billable=Sum('optima_billable'),
        total_optima_non_billable=Sum('optima_non_billable'),
        total_office_rent=Sum('office_rent'),
        total_others=Sum('others'),
        total_advance_due=Sum('advance_due'),
        total_zone_cost=Sum('total_zone_cost'),
        total_balance_forward=Sum('balance_forward'),
        total_tt=Sum('total_tt'),
        total_run_hour=Sum('total_run_hour'),   
     ).order_by('region', 'zone','-created_at')

    region_data = {}
    for data in region_zone_data:
        region = data['region']
        if region not in region_data:
            region_data[region] = []
        region_data[region].append(data)
    context = {
        'region_data': region_data,
    }
    return render(request, 'expenses/grand_summary_expenses/view_summary_expenses.html', context)



@login_required
def update_summary_expenses(request, summary_expenses_id):
    summary_expenses = SummaryExpenses.objects.get(id=summary_expenses_id)
    if request.method == 'POST':
        form = SummaryExpensesForm(request.POST, instance=summary_expenses)
        if form.is_valid():
            total_run_hour = form.cleaned_data.get('total_run_hour')
            if total_run_hour is None:
                form.add_error('total_run_hour', 'Total Run Hour cannot be empty.')
            else:
                form.save()
                return redirect('dailyexpense:zone_wise_expenses_view')
    else:
        form = SummaryExpensesForm(instance=summary_expenses)
    return render(request, 'expenses/grand_summary_expenses/update_summary_report.html', {'form': form})

