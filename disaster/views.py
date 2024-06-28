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

from .forms import MoneyRequisitionForm,MoneySendingForm,ExpenseRequisitionStatusForm
from .models import DisasterMoneyRequisition

from common.models import FuelPumpDatabase,PGTLdatabase
from tickets.forms import SummaryReportChartForm
from tickets.models import eTicket,PGRdatabase
from tickets.views import generate_unique_finance_requisition_number


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



def disaster_advance_management(request):
    return render(request,'disaster/expense_advance_management.html')# for expense and advance management dashboard shortcut



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
            return redirect('disaster:all_approval_status')
    else:     
        form = MoneyRequisitionForm()
    return render(request, 'disaster/money_requisition/money_requisition_form.html', {'form': form})



@login_required
def all_approval_status(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None
    region_approvals = None
    zone_approvals = None

    form = ExpenseRequisitionStatusForm(request.GET or {'days': 20})
    money_requisitions = DisasterMoneyRequisition.objects.all().order_by('-created_at')

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')

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
        if mp:
            money_requisitions = money_requisitions.filter(mp=mp)

        # Calculate region-wise and zone-wise summaries
        region_approvals = money_requisitions.values('region').annotate(
            total_requisition=Sum('requisition_amount'),
            total_approved=Sum('approved_amount'),
            num_requisitions=Count('id')
        ).order_by('region')

        zone_approvals = money_requisitions.values('zone').annotate(
            total_requisition=Sum('requisition_amount'),
            total_approved=Sum('approved_amount'),
            num_requisitions=Count('id')
        ).order_by('zone')

    # Pagination logic
    page_obj = None
    money_per_page = 2
    paginator = Paginator(money_requisitions, money_per_page)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    
    form = ExpenseRequisitionStatusForm()
    return render(request, 'disaster/money_requisition/approval_history.html', {
        'money_requisitions':money_requisitions,
        'page_obj': page_obj,
        'region_approvals': region_approvals,
        'zone_approvals': zone_approvals,
        'days': days,
        'form': form,
        'start_date': start_date,
        'end_date': end_date
    })



@login_required
def requisition_approval(request, requisition_id):
    requisition = get_object_or_404(DisasterMoneyRequisition, id=requisition_id)
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
                 return redirect('disaster:requisition_approval', requisition_id=requisition_id)
            
            
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

            return redirect('disaster:all_approval_status')
        else:
            return render(request, 'expenses/money_requisition/money_approval_form.html', {'requisition': requisition})
    else:        
        messages.error(request, "You can not get access at this moment. May be due to previous level approval is pending or you are not authorized from your management")
        return redirect('disaster:all_approval_status')




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
  
    requisitions = DisasterMoneyRequisition.objects.all()
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
    requisition = get_object_or_404(DisasterMoneyRequisition, id=requisition_id)
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
            return redirect('disaster:all_approval_status')

    else:     
        form = MoneySendingForm()
    return render(request, 'disaster/money_requisition/money_requisition_form.html', {'form': form})







@login_required
def mark_received(request, requisition_id): 
    requisition = get_object_or_404(DisasterMoneyRequisition, id=requisition_id)   
    if requisition.requester == request.user:      
        requisition.receiving_status = 'Received'
        requisition.save()
        messages.success(request, 'Requisition marked as received successfully.')
    else:
        messages.error(request, 'You are not authorized to mark this requisition as received.')

    return redirect('disaster:all_approval_status')



