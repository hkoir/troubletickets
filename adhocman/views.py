
from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse,HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg,Count,Q,Case, When, IntegerField,F,Max,DurationField, DecimalField
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from.forms import AdhocRequisitionForm,AdhocRequisitionStatusForm
from common.models import PGRdatabase
from.models import AdhocRequisition,AdhocPayment,AdhocAttendance

from datetime import datetime,timedelta
from django.utils import timezone
from decimal import Decimal
import xlsxwriter

from .forms import AdhocAttendanceIntimeForm,AdhocAttendanceUpdateOuttimeForm,AdhocPaymentForm
from django.core.exceptions import ValidationError

def adhoc_management_dashboard(request):
    return render(request,'adhocman/adhoc_man_management.html')# for expense and advance management dashboard shortcut



from dailyexpense.views import generate_unique_finance_requisition_number
def create_adhoc_requisition(request):
    if request.method == 'POST':
        form = AdhocRequisitionForm(request.POST)
        if form.is_valid():
            form.instance.requester = request.user
            form.instance.requisition_id = generate_unique_finance_requisition_number()
            form.save()
            form = AdhocRequisitionForm()
            return redirect('adhocman:create_adhoc_requisition')
            
    else:
        form = AdhocRequisitionForm()
    
    adhoc_requisitions = AdhocRequisition.objects.all().order_by('-created_at')
    return render(request, 'adhocman/create_adhoc_requisition.html', {
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
    adhoc_requisitions = AdhocRequisition.objects.all().order_by('-created_at')

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
            adhoc_requisitions = adhoc_requisitions.filter(pgr__region=region)
        if zone:
            adhoc_requisitions = adhoc_requisitions.filter(pgr__zone=zone)
        if mp:
            adhoc_requisitions = adhoc_requisitions.filter(pgr__mp=mp)

        # Calculate region-wise and zone-wise summaries
        region_approvals = adhoc_requisitions.values('pgr__region').annotate(
         total_requisition=Sum('num_of_days_applied'),
        total_approved=Sum('num_of_days_approved')
            ).order_by('pgr__region')

     

        zone_approvals = adhoc_requisitions.values('pgr__zone').annotate(
            total_requisition=Sum('num_of_days_applied'),
            total_approved=Sum(
                Case(
                    When(approval_status='APPROVED', then=F('num_of_days_approved')),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by('pgr__zone')
   



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
    return render(request, 'adhocman/approval_status.html', {
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
    requisition = get_object_or_404(AdhocRequisition, id=requisition_id)
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
                return redirect('adhocman:adhoc_management_approval', requisition_id=requisition_id)
            
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

            return redirect('adhocman:adhoc_approval_status')
        else:
            return render(request, 'adhocman/adhoc_approval_form.html', {'requisition': requisition})
    else:        
        messages.error(request, "You cannot get access at this moment. This may be due to the previous level approval being pending or you not being authorized from your management")
        return redirect('adhocman:adhoc_approval_status')






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
  
    requisitions = AdhocRequisition.objects.all()
    for row, requisition in enumerate(requisitions, start=1):
        update_at_str = timezone.localtime(requisition.update_at).strftime('%Y-%m-%d %H:%M:%S')
      
        worksheet.write(row, 0, str(update_at_str))
        worksheet.write(row, 1, str(requisition.num_of_days))      
     

    workbook.close()
    return response



@login_required
def adhoc_intime(request):
    adhoc_attendance = AdhocAttendance.objects.all().order_by('-created_at')
    if request.method == 'POST':
        form = AdhocAttendanceIntimeForm(request.POST)
        if form.is_valid():
            adhoc_instance = form.save(commit=False)
            adhoc_instance.save()
            messages.success(request, 'Adhoc intime has been successfully recorded.')
            return redirect('adhocman:adhoc_intime')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = AdhocAttendanceIntimeForm()

    return render(request, 'adhocman/adhoc_intime.html', {'form': form, 'adhoc_attendance': adhoc_attendance})


@login_required
def adhoc_outtime(request, attendance_id):
    adhoc_attendance = AdhocAttendance.objects.all().order_by('-created_at')
    adhoc_instance = get_object_or_404(AdhocAttendance, id=attendance_id)
    if request.method == 'POST':
        form = AdhocAttendanceUpdateOuttimeForm(request.POST, instance=adhoc_instance)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Adhoc outtime has been successfully updated.')
                return redirect('adhocman:adhoc_intime')
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AdhocAttendanceUpdateOuttimeForm(instance=adhoc_instance)

    return render(request, 'adhocman/adhoc_intime.html', {'form': form, 'adhoc_instance': adhoc_instance, 'adhoc_attendance': adhoc_attendance})





@login_required
def view_adhoc_attendance(request):
    adhoc_attendance_data = AdhocAttendance.objects.all().order_by('-created_at')
    print(adhoc_attendance_data)  # Debug statement to check if the queryset is not empty
    for adhoc in adhoc_attendance_data:
        if adhoc.adhoc_payment and adhoc.adhoc_payment.transaction_id:
            print(adhoc.adhoc_payment.transaction_id)
        else:
            print('nothing')
    return render(request, 'adhocman/view_adhoc_attendance.html', {'adhoc_attendance_data': adhoc_attendance_data})



@login_required
def create_adhoc_payment(request, adhoc_attendance_id):
    adhoc_attendance = get_object_or_404(AdhocAttendance, id=adhoc_attendance_id)
    if request.method == 'POST':
        form = AdhocPaymentForm(request.POST, request.FILES)
        if form.is_valid():
            adhoc_payment = form.save(commit=False)
            adhoc_payment.pgr = adhoc_attendance.pgr
            adhoc_payment.save()
            # Ensure the AdhocPayment instance is assigned to adhoc_payment
            adhoc_attendance.adhoc_payment = adhoc_payment
            adhoc_attendance.save()
            messages.success(request, 'Adhoc payment has been successfully recorded.')
            return redirect('adhocman:view_adhoc_attendance')
        else:
            messages.error(request, 'There was an error with your submission.')
    else:
       form = AdhocPaymentForm(initial={'pgr': adhoc_attendance.pgr})
    return render(request, 'adhocman/create_adhoc_payment.html', {'form': form, 'adhoc_attendance': adhoc_attendance})
