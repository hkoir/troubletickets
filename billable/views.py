
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse,JsonResponse

from .forms import CivilPowerRequisition
from django.contrib import messages
from django.db.models import Sum, Avg,Count,Q,Case, When, IntegerField,F,Max,DurationField, DecimalField,FloatField
from django.contrib.auth.decorators import login_required
from tickets.views import generate_unique_finance_requisition_number
from.models import CivilPower,ChatMessage
from.forms import ExpenseRequisitionStatusForm,ChatForm,MoneySendingForm,WorkUpdateForm

from datetime import datetime,timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from decimal import Decimal
import xlsxwriter





def billable_dashboard(request):
    return render(request, 'billable/billable_dashboard.html')



@login_required
def chat(request, ticket_id):
    ticket = get_object_or_404(CivilPower, pk=ticket_id)
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket_id = ticket_id
            message.ticket = ticket 
            message.sender = request.user.name
            message.timestamp = timezone.now()
            message.save()
            return redirect('billable:chat', ticket_id=ticket_id)
    else:
        form = ChatForm()
    messages = ChatMessage.objects.filter(ticket_id=ticket_id).order_by('timestamp')
    return render(request, 'billable/tchat.html', {'ticket': ticket, 'messages': messages, 'form': form})




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
def civil_power_requisition(request):
    if request.method == 'POST':   
        form = CivilPowerRequisition(request.POST, request.FILES)
        if form.is_valid():        
            form.instance.requester = request.user
            form.instance.requisition_number = generate_unique_finance_requisition_number()
            form.save()
            return redirect('billable:civil_power_approval_status')
    else:     
        form = CivilPowerRequisition()
    return render(request, 'billable/money_requisition_form.html', {'form': form})




@login_required
def civil_power_approval_status(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    region_approvals = None
    zone_approvals = None

    form = ExpenseRequisitionStatusForm(request.GET or {'days': 30})
    money_requisitions = CivilPower.objects.all().order_by('-created_at')

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')


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
    return render(request, 'billable/approval_history.html', {
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
    requisition = get_object_or_404(CivilPower, id=requisition_id)
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
                 return redirect('billable:requisition_approval', requisition_id=requisition_id)
            
            
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

            return redirect('billable:civil_power_approval_status')
        else:
            return render(request, 'billable/money_approval_form.html', {'requisition': requisition})
    else:        
        messages.error(request, "You can not get access at this moment. May be due to previous level approval is pending or you are not authorized from your management")
        return redirect('billable:civil_power_approval_status')





@login_required
def  civil_power_approval_status2(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    region_approvals = None
    zone_approvals = None

    form = ExpenseRequisitionStatusForm(request.GET or {'days': 30})
    money_requisitions = CivilPower.objects.all().order_by('-created_at')

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')


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
    return render(request, 'billable/approval_history2.html', {
        'money_requisitions':money_requisitions,
        'page_obj': page_obj,
        'region_approvals': region_approvals,
        'zone_approvals': zone_approvals,
        'days': days,
        'form': form,
        'start_date': start_date,
        'end_date': end_date
    })



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
def requisition_approval2(request, requisition_id):
    requisition = get_object_or_404(CivilPower, id=requisition_id)

    # Determine the required level based on the current approval status
    if requisition.level1_approval_status == 'PENDING':
        required_level = 'first_level'
    elif requisition.level2_approval_status == 'PENDING':
        required_level = 'second_level'
    elif requisition.level3_approval_status == 'PENDING':
        required_level = 'third_level'
    else:  
        return JsonResponse({"message": "Requisition already approved by all levels"}, status=400)

    @manager_level_required2(required_level)
    def process_approval(request):
        if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            approval_status = request.POST.get('approval_status')
            approved_amount = request.POST.get('approved_amount')
            approval_date = timezone.now()

            if required_level == 'first_level' and requisition.level1_approval_status == 'PENDING':
                requisition.approved_amount = approved_amount
                requisition.level1_approval_date = approval_date
                requisition.level1_approval_status = approval_status
            elif required_level == 'second_level' and requisition.level2_approval_status == 'PENDING':
                requisition.approved_amount = approved_amount
                requisition.level2_approval_status = approval_status
                requisition.level2_approval_date = approval_date
            elif required_level == 'third_level' and requisition.level3_approval_status == 'PENDING':
                requisition.approved_amount = approved_amount
                requisition.level3_approval_status = approval_status
                requisition.level3_approval_date = approval_date
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
  
    requisitions = CivilPower.objects.all()
    for row, requisition in enumerate(requisitions, start=1):
        update_at_str = timezone.localtime(requisition.update_at).strftime('%Y-%m-%d %H:%M:%S')
      
        worksheet.write(row, 0, str(update_at_str))
        worksheet.write(row, 1, str(requisition.requisition_number))      
        worksheet.write(row, 2, str(requisition.requester))
        worksheet.write(row, 3, str(requisition.region))
        worksheet.write(row, 4, str(requisition.zone))
   
        worksheet.write(row, 5, requisition.task_name)
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
def upload_money_sending_doc(request,requisition_id):
    requisition = get_object_or_404(CivilPower, id=requisition_id)
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
            return redirect('billable:civil_power_approval_status')

    else:     
        form = MoneySendingForm()
    return render(request, 'expenses/money_requisition/money_requisition_form.html', {'form': form})



@login_required
def update_work(request,requisition_id):
    requisition = get_object_or_404(CivilPower, id=requisition_id)
    if request.method == 'POST':
        form = WorkUpdateForm(request.POST, request.FILES)
        if form.is_valid():          

            if form.cleaned_data['UploadPicture'] and form.cleaned_data['TakePicture']:
                print('Please select only one option for picture')
                form.add_error('UploadPicture', 'Please select only one option for picture')
                form.add_error('TakePicture', 'Please select only one option for picture')
            elif form.cleaned_data['UploadPicture']:
                requisition.task_completion_image = form.cleaned_data['UploadPicture']
            elif form.cleaned_data['TakePicture']:
                requisition.task_completion_image = form.cleaned_data['TakePicture']

            requisition.TT_status = form.cleaned_data.get('TT_status')
            requisition.work_completion_date = form.cleaned_data.get('work_completion_date')
            requisition.TT_close_date = form.cleaned_data.get('TT_close_date')
            requisition.actual_cost = form.cleaned_data.get('actual_cost')
                      
            requisition.save()
            return redirect('billable:civil_power_approval_status')

    else:     
        form = WorkUpdateForm()
    return render(request, 'billable/work_update.html', {'form': form})





@login_required
def mark_received(request, requisition_id): 
    requisition = get_object_or_404(CivilPower, id=requisition_id)   
    if requisition.requester == request.user:      
        requisition.receiving_status = 'Received'
        requisition.save()
        messages.success(request, 'Requisition marked as received successfully.')
    else:
        messages.error(request, 'You are not authorized to mark this requisition as received.')

    return redirect('billable:civil_power_approval_status')

