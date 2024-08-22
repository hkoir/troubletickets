
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
from dailyexpense.views import generate_unique_finance_requisition_number

from django.db.models import OuterRef, Subquery, Value, CharField,Sum, Value, DecimalField, DurationField, F, ExpressionWrapper,FloatField
from django.conf import settings

from django.utils.dateparse import parse_date
from.forms import PGRNameForm
from tickets.models import eTicket
from django.db.models.functions import Coalesce, Round




def adhoc_management_dashboard(request):
    return render(request,'adhocman/adhoc_man_management.html')# for expense and advance management dashboard shortcut



@login_required
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
    paginator = Paginator(adhoc_requisitions, 5)  # Show 10 requisitions per page.
    page_number = request.GET.get('page')

    try:
        adhoc_requisitions = paginator.page(page_number)
    except PageNotAnInteger:
        adhoc_requisitions = paginator.page(1)
    except EmptyPage:
        adhoc_requisitions = paginator.page(paginator.num_pages)

    return render(request, 'adhocman/create_adhoc_requisition.html', {
        'form': form,
        'adhoc_requisitions': adhoc_requisitions,
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
                    When(level1_approval_status='Approved', then=F('num_of_days_approved')),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by('pgr__zone')
   

    # Pagination logic
    page_obj = None 
    paginator = Paginator(adhoc_requisitions, 5)
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
                    When(level1_approval_status='Approved', then=F('num_of_days_approved')),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by('pgr__zone')
   

    # Pagination logic
    page_obj = None 
    paginator = Paginator(adhoc_requisitions, 5)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)


  
    form = AdhocRequisitionStatusForm()
    return render(request, 'adhocman/approval_status2.html', {
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
    requisition = get_object_or_404(AdhocRequisition, id=requisition_id)

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
          form.save()
          messages.success(request, 'Adhoc intime has been successfully recorded.')
          return redirect('adhocman:adhoc_intime')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = AdhocAttendanceIntimeForm()

    return render(request, 'adhocman/adhoc_intime.html', {'form': form, 'adhoc_attendance': adhoc_attendance})




from django.http import JsonResponse
@login_required
def fetch_requisitions(request, pgr_id):
    print(f"Fetching requisitions for PGR ID: {pgr_id}")
    requisitions = AdhocRequisition.objects.filter(
        pgr_id=pgr_id,      
        level1_approval_status='Approved'
    ).values('id', 'name')
    print(f"Requisitions found: {list(requisitions)}")
    return JsonResponse(list(requisitions), safe=False)




@login_required
def adhoc_outtime(request, attendance_id):
    adhoc_attendance = AdhocAttendance.objects.all().order_by('-created_at')
    adhoc_instance = get_object_or_404(AdhocAttendance, id=attendance_id)
    if request.method == 'POST':
        form = AdhocAttendanceUpdateOuttimeForm(request.POST, instance=adhoc_instance)
        if form.is_valid():
            try:
                adhoc_instance = form.save(commit=False)
                if adhoc_instance.adhoc_requisition:
                    adhoc_instance.adhoc_requisition.active_status = False
                    adhoc_instance.adhoc_requisition.save()
                    print("Adhoc Requisition active_status set to False and saved.")
                else:
                    print("No associated adhoc_requisition found.")
                adhoc_instance.save()
                messages.success(request, 'Adhoc outtime has been successfully updated.')
                return redirect('adhocman:adhoc_intime')
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = AdhocAttendanceUpdateOuttimeForm(instance=adhoc_instance)

    return render(request, 'adhocman/adhoc_intime.html', {'form': form, 'adhoc_instance': adhoc_instance, 'adhoc_attendance': adhoc_attendance})




@login_required
def adhoc_outtime2(request, attendance_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        adhoc_instance = get_object_or_404(AdhocAttendance, id=attendance_id)
        
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
def view_adhoc_attendance2(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None
    form = AdhocRequisitionStatusForm(request.GET or None)
    adhoc_attendance_data = AdhocAttendance.objects.all().order_by('-created_at')


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
            adhoc_attendance_data = adhoc_attendance_data.filter(pgr__region=region)
        if zone:
           adhoc_attendance_data = adhoc_attendance_data.filter(pgr__zone=zone)
        if mp:
            adhoc_attendance_data = adhoc_attendance_data.filter(pgr__mp=mp)


    
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
    return render(request, 'adhocman/view_adhoc_attendance2.html',
             {
            'adhoc_attendance_data': adhoc_attendance_data,
            'start_date':start_date,
            'end_start':end_date,
            'days':days,
            'form':form,
            'page_obj':page_obj,

            })


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .forms import AdhocRequisitionStatusForm
from .models import AdhocAttendance
from datetime import datetime, timedelta

@login_required
def view_adhoc_attendance(request):
    start_date=None
    end_date=None
    days = None

    form = AdhocRequisitionStatusForm(request.GET or None)
    adhoc_attendance_data = AdhocAttendance.objects.all().order_by('pgr')

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        pgr = request.GET.get('pgr')

        if start_date and end_date:
            adhoc_attendance_data = adhoc_attendance_data.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            adhoc_attendance_data = adhoc_attendance_data.filter(created_at__range=(start_date, end_date))

        if region:
            adhoc_attendance_data = adhoc_attendance_data.filter(pgr__region=region)
        if zone:
            adhoc_attendance_data = adhoc_attendance_data.filter(pgr__zone=zone)
        if mp:
            adhoc_attendance_data = adhoc_attendance_data.filter(pgr__mp=mp)
        if pgr:
            adhoc_attendance_data = adhoc_attendance_data.filter(pgr__name=pgr)

     

    # Pagination logic
    paginator = Paginator(adhoc_attendance_data, 5)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    form = AdhocRequisitionStatusForm()
    return render(request, 'adhocman/view_adhoc_attendance.html', {
        'adhoc_attendance_data': page_obj,  # Pass paginated data
        'start_date': start_date,
        'end_start': end_date,
        'days': days,
        'form': form,
        'page_obj': page_obj,
        'adhoc_attendance_data':adhoc_attendance_data
    })



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







@login_required
def pay_pgr_by_name(request):
    if request.method == 'POST':
        form = PGRNameForm(request.POST)
        if form.is_valid():
            pgr_name = form.cleaned_data['pgr_name']
            try:
                # Retrieve the latest AdhocAttendance for the given PGR name
                pgr = PGRdatabase.objects.get(name=pgr_name)
                adhoc_attendance = AdhocAttendance.objects.filter(pgr=pgr).order_by('-created_at').first()
                if adhoc_attendance:
                    return redirect('adhocman:create_adhoc_payment', adhoc_attendance_id=adhoc_attendance.id)
                else:
                    messages.error(request, 'No attendance record found for the given PGR.')
            except PGRdatabase.DoesNotExist:
                messages.error(request, 'PGR with the given name does not exist.')
        else:
            messages.error(request, 'Invalid form submission.')
    else:
        form = PGRNameForm()

    return render(request, 'adhocman/pay_pgr_by_name.html', {'form': form})




@login_required
def adhoc_summary_view(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None
    form = AdhocRequisitionStatusForm(request.GET)
    adhoc_summary = AdhocAttendance.objects.all()
  

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        pgr = request.GET.get('pgr')

        if start_date and end_date:
            adhoc_summary = adhoc_summary.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            adhoc_summary = adhoc_summary.filter(created_at__range=(start_date, end_date))

        if region:
            adhoc_summary = adhoc_summary.filter(pgr__region=region)
        if zone:
            adhoc_summary = adhoc_summary.filter(pgr__zone=zone)
        if mp:
            adhoc_summary = adhoc_summary.filter(pgr__mp=mp)
        if pgr:
            adhoc_summary = adhoc_summary.filter(pgr__name=pgr)

    # Convert internal_generator_running_hours to seconds
    internal_generator_running_hours = ExpressionWrapper(
        F('adhoc_ticket__internal_generator_running_hours') / timedelta(seconds=1),  # Convert duration to hours
        output_field=FloatField()
    )

    adhoc_summary = adhoc_summary.values(
        'pgr__id', 'pgr__name', 'pgr__region', 'pgr__zone', 'pgr__mp'
    ).annotate(      
        total_working_hours=Sum('adhoc_working_hours'),
        total_bill_amount=Sum('adhoc_bill_amount'),
        adhoc_paid_amount=Coalesce(Sum('adhoc_payment__adhoc_paid_amount'), Value(0, output_field=DecimalField())),
        total_internal_generator_running_hours=Coalesce(Sum(internal_generator_running_hours), Value(0, output_field=FloatField())),
        total_TT_handle=Coalesce(Count('pgr_id'), Value(0, output_field=IntegerField())),
    ).order_by('pgr__name')



    # Adjust values if needed
    for summary in adhoc_summary:
        summary['adhoc_net_payment_due'] = summary['total_bill_amount'] - summary['adhoc_paid_amount']

    form = AdhocRequisitionStatusForm()
    return render(request, 'adhocman/adhoc_bill_summary.html', {
        'adhoc_summary': adhoc_summary,
        'MEDIA_URL': settings.MEDIA_URL,
        'form': form,
      
    })




from .forms import PGRPaymentForm
@login_required
def adhoc_pgr_grand_summary(request):
    days = None
    start_date = None
    end_date = None
    region = None
    zone = None
    mp = None
    number_of_days = None 
    aggregated_data = {}
    total_bill_paid=None
   

    form = AdhocRequisitionStatusForm(request.GET or {'days':30})  
    adhoc_man_payment_data =AdhocPayment.objects.all()
    adhoc_man_attendance_data =AdhocAttendance.objects.all()
    adhoc_ticket_data = eTicket.objects.all()

  
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        days = form.cleaned_data.get('days')
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')
        pgr = form.cleaned_data.get('pgr')
        
        if start_date and end_date:            
            adhoc_man_payment_data = adhoc_man_payment_data.filter(created_at__range=(start_date, end_date))
            adhoc_ticket_data = adhoc_ticket_data.filter(created_at__range=(start_date, end_date))
            adhoc_man_attendance_data = adhoc_man_attendance_data.filter(created_at__range=(start_date, end_date))
        elif days:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            adhoc_man_payment_data = adhoc_man_payment_data.filter(created_at__range=(start_date, end_date))
            adhoc_ticket_data = adhoc_ticket_data.filter(created_at__range=(start_date, end_date))
            adhoc_man_attendance_data = adhoc_man_attendance_data.filter(created_at__range=(start_date, end_date))
                        
        if pgr:
           
            adhoc_man_payment_data = adhoc_man_payment_data.filter(pgr__name=pgr)
            adhoc_ticket_data = adhoc_ticket_data.filter(assigned_to__name=pgr)
            adhoc_man_attendance_data = adhoc_man_attendance_data.filter(pgr__name=pgr)

        if region:
            adhoc_man_payment_data = adhoc_man_payment_data.filter(pgr__region=region)
            adhoc_ticket_data = adhoc_ticket_data.filter(region=region)
            adhoc_man_attendance_data = adhoc_man_attendance_data.filter(pgr__region=region)

        if zone:
            adhoc_man_payment_data = adhoc_man_payment_data.filter(pgr__zone=zone)
            adhoc_ticket_data = adhoc_ticket_data.filter(zone=zone)
            adhoc_man_attendance_data = adhoc_man_attendance_data.filter(pgr__zone=zone)

        if mp:
            adhoc_man_payment_data = adhoc_man_payment_data.filter(pgr__mp=mp)
            adhoc_ticket_data = adhoc_ticket_data.filter(mp=mp)
            adhoc_man_attendance_data = adhoc_man_attendance_data.filter(pgr__mp=mp)

       
        for attendance in adhoc_man_attendance_data:
            if attendance.pgr and attendance.pgr.name:
                adhoc_working_hours  = attendance.adhoc_working_hours     
                adhoc_bill_amount =attendance.adhoc_bill_amount
             
                pgr = attendance.pgr.name if attendance.pgr else "Unknown PGR"
                pgtl = attendance.pgr.pgtl.name if attendance.pgr.pgtl else "Unknown PGTL"
                pgr_region = attendance.pgr.region if attendance.pgr.region else "Unknown Region"  
                pgr_zone = attendance.pgr.zone if attendance.pgr.zone else "Unknown Zone"                    
                pgr_mp = attendance.pgr.mp if attendance.pgr.mp else "Unknown MP" 

                pgr_phone = attendance.pgr.phone if attendance.pgr.phone else "Unknown phone"  
                pgr_payment_number = attendance.pgr.payment_number if attendance.pgr.payment_number else "Unknown number"
                pgr_payment_option = attendance.pgr.payment_number_choice if attendance.pgr.payment_number_choice else "Unknown option choices"                      
                team_leader_phone = attendance.pgr.pgtl.phone if attendance.pgr.pgtl.phone else "Unknown phone" 


                 
                
                        
                if pgr not in aggregated_data:
                    aggregated_data[pgr] = {
                        'pgr_id': attendance.pgr.id,
                        'total_working_hours': 0,
                        'total_bill_amount': 0,
                        'total_bill_paid': 0,
                        'total_tickets_handle': 0,
                        'total_pg_runhour_handle': 0,
                        'region': pgr_region,
                        'zone': pgr_zone,
                        'mp': pgr_mp,
                        'pgtl':pgtl,

                        'pgr_phone':pgr_phone,
                        'pgr_payment_number':pgr_payment_number,
                        'pgr_payment_option': pgr_payment_option,
                        'team_leader_phone':team_leader_phone,

                    }

                if adhoc_working_hours:
                     aggregated_data[pgr]['total_working_hours'] += adhoc_working_hours
                if adhoc_bill_amount:
                     aggregated_data[pgr]['total_bill_amount'] +=adhoc_bill_amount          
               
        for payment_data in adhoc_man_payment_data:      
            if payment_data.pgr:
                pgr = payment_data.pgr.name             
                total_bill_paid = payment_data.adhoc_paid_amount
            if pgr in aggregated_data:
                if total_bill_paid:
                    aggregated_data[pgr]['total_bill_paid'] += Decimal(total_bill_paid)         
   
        for ticket_data in adhoc_ticket_data:          
            if ticket_data.assigned_to:
                pgr = ticket_data.assigned_to.name
                total_pg_runhour_handle = ticket_data.internal_generator_running_hours.total_seconds() / 3600 if isinstance(ticket_data.internal_generator_running_hours, timedelta) else ticket_data.internal_generator_running_hours
                if pgr in aggregated_data:                
                    aggregated_data[pgr]['total_tickets_handle'] += 1
                    aggregated_data[pgr]['total_pg_runhour_handle'] += total_pg_runhour_handle

        for summary in aggregated_data.values():
            summary['adhoc_net_payment_due'] = summary['total_bill_amount'] - summary['total_bill_paid']

       
    aggregated_data_list = list(aggregated_data.items())
    paginator = Paginator(aggregated_data_list, 10)
    page_number = request.GET.get('page')

    try:
        aggregated_data_page = paginator.page(page_number)
    except PageNotAnInteger:
        aggregated_data_page = paginator.page(1)
    except EmptyPage:
        aggregated_data_page = paginator.page(paginator.num_pages)

    form = AdhocRequisitionStatusForm()
    context = {
        'aggregated_data_page': aggregated_data_page,
        'form': form,
        'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'number_of_days': number_of_days,
      
    }

    return render(request, 'adhocman/adhoc_pgr_grand_sum.html', context)

@login_required
def create_adhoc_payment_common(request):  
    if request.method == 'POST':
        form = AdhocPaymentForm(request.POST, request.FILES)
        if form.is_valid():           
            form.save()
            messages.success(request, 'Adhoc payment has been successfully recorded.')
            return redirect('adhocman:view_adhoc_attendance')
        else:
            messages.error(request, 'There was an error with your submission.')
    else:
       form = AdhocPaymentForm()
    return render(request, 'adhocman/create_adhoc_payment.html', {'form': form})


@login_required
def single_adhoc_payment_view(request, payment_id):
    adhoc_payment = get_object_or_404(AdhocPayment, id=payment_id)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = parse_date(start_date)
    if end_date:
        end_date = parse_date(end_date)

    if start_date and end_date:
        payments = AdhocPayment.objects.filter(
            pgr=adhoc_payment.pgr,
            created_at__range=(start_date, end_date)
        )
    else:
        payments = AdhocPayment.objects.filter(pgr=adhoc_payment.pgr)

    return render(request, 'adhocman/single_adhoc_payment.html', {
        'payments': payments,
        'adhoc_payment': adhoc_payment,
        'start_date': start_date,
        'end_date': end_date,
    })
