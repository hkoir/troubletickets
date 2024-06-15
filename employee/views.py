from django.shortcuts import render, redirect,get_object_or_404, redirect
from django.http import HttpResponse
from openpyxl import Workbook
from io import BytesIO
import os

from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib import messages
from django.templatetags.static import static
from django.conf import settings

from django.db.models import F, ExpressionWrapper, FloatField, Sum,Avg,Count,Q,Case, When, IntegerField
from django.db.models import Subquery, OuterRef

from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4,letter
from reportlab.pdfgen import canvas

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import EmployeeModel, AttendanceModel,MonthlySalaryReport,EmployeeRecordChange,Resource
from .forms import AddEmployeeForm,AttendanceForm,EditAttendanceForm,AddEmployeeForm,MonthYearForm,CreateResurceForm

from generator.models import AddPGInfo
from tickets.forms import SummaryReportChartForm




def human_resource_management(request):
    return render(request,'employee/human_resource_management.html')



@login_required
def add_employee(request):
    if request.method == 'POST':
        form = AddEmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()         
            return redirect('employee:view_employee')
        else:
            print(form.errors)  
    else:
        form = AddEmployeeForm()    
    return render(request, 'employee/add_employee_form.html', {'form': form})



@login_required
def view_employee(request):
    employee_records = EmployeeModel.objects.all()

    paginator = Paginator(employee_records, 10) 
    page_number = request.GET.get('page')

    try:
        employee_records = paginator.page(page_number)
    except PageNotAnInteger:
        employee_records = paginator.page(1)
    except EmptyPage:
       employee_records = paginator.page(paginator.num_pages)

    return render(request, 'employee/view_employee.html', {'employee_records': employee_records})




@login_required
def update_employee(request, employee_id):
    employee = get_object_or_404(EmployeeModel, id=employee_id)
    print(employee)
    if request.method == 'POST':
        form = AddEmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee:view_employee')  # Redirect to the view employee page
    else:
        form = AddEmployeeForm(instance=employee)
    return render(request, 'employee/add_employee_form.html', {'form': form})


@login_required
def delete_employee(request, employee_id):
    employee = get_object_or_404(EmployeeModel, id=employee_id)
    if request.method == 'POST':
        if request.POST.get('confirm') == 'yes': 
            employee.delete()
            messages.success(request, 'Employee deleted successfully.')
            return redirect('employee:view_employee')  
        else:
            return redirect('employee:view_employee')

    return render(request, 'employee/delete_record.html', {'employee': employee})




@login_required
@receiver(pre_save, sender=EmployeeModel)
def log_employee_changes(sender, instance, **kwargs):
    if instance.pk:
        old_instance = EmployeeModel.objects.get(pk=instance.pk)
        for field in instance._meta.fields:
            old_value = getattr(old_instance, field.attname)
            new_value = getattr(instance, field.attname)
            if old_value != new_value:
                EmployeeRecordChange.objects.create(
                    employee=instance,
                    field_name=field.attname,
                    old_value=str(old_value),
                    new_value=str(new_value)
                )




@login_required
def view_employee_changes(request): 
    changes = EmployeeRecordChange.objects.all()
    return render(request, 'employee/employee_change_record.html', {'changes': changes})


@login_required
def view_employee_changes_single(request, employee_id): 
    employee = get_object_or_404(EmployeeModel, pk=employee_id)
    changes_single = EmployeeRecordChange.objects.filter(employee=employee)
    return render(request, 'employee/employee_change_record.html', {'changes_single': changes_single})




@login_required
def download_employee_changes(request): 
    employee_changes = EmployeeRecordChange.objects.all()
    workbook = Workbook()
    worksheet = workbook.active
    headers = ['Employee ID', 'Field Name', 'Old Value', 'New Value']
    worksheet.append(headers)

    for change in employee_changes:
        row = [change.employee_id, change.field_name, change.old_value, change.new_value]
        worksheet.append(row)

    excel_file = BytesIO()
    workbook.save(excel_file)
    excel_file.seek(0)

    response = HttpResponse(
        excel_file.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=employee_changes.xlsx'

    return response


def attendance_input(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()         
            return redirect('employee:view_attendance')
        else:
            print(form.errors)  # Print form errors for debugging
    else:
        form = AttendanceForm()    
    return render(request, 'employee/attendance_form.html', {'form': form})




@login_required
def view_attendance(request):
    attendance_records = AttendanceModel.objects.all()
    return render(request, 'employee/view_attendance.html', {'attendance_records': attendance_records})


@login_required
def update_attendance(request, employee_id):
    employee = get_object_or_404(AttendanceModel, id=employee_id) 
    print(employee)  
    if request.method == 'POST':
        form =  EditAttendanceForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee:view_attendance')  
    else:
        form =  EditAttendanceForm(instance=employee)
    return render(request, 'employee/attendance_form.html', {'form': form,'employee':employee})



month =None
year = None
@login_required
def create_salary(request):
    global month, year  
    
    if 'month' in request.GET:
        month = int(request.GET['month'])     

    if 'year' in request.GET:
        year = int(request.GET['year']) 

        employees = EmployeeModel.objects.all()
        for employee in employees:
            total_salary = (
                employee.basic_salary +
                employee.house_allowance +
                employee.medical_allowance +
                employee.transportation_allowance +
                employee.bonus
            )
            MonthlySalaryReport.objects.update_or_create(
                employee=employee,
                month=month,
                year=year,
                defaults={'total_salary': total_salary}
            )         
        return redirect('employee:create_salary')
    else:
        form = MonthYearForm()   
   
    salary = MonthlySalaryReport.objects.filter(month = month, year =year)
    context = {'form': form, 'salary': salary,'month':month, 'year':year}
    return render(request, 'employee/create_monthly_salary.html', context)



def generate_salary_sheet(month, year):  
    salary_reports = MonthlySalaryReport.objects.filter(month=month, year=year)
    salary_sheet = []  
    for report in salary_reports:
        employee = report.employee
        total_salary = report.total_salary
        salary_sheet.append({'employee': employee, 'total_salary': total_salary})

    return salary_sheet


@login_required
def download_salary(request):
    global month,year
    salary_sheet = generate_salary_sheet(month, year)  

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Salary Report'
  
    headers = ['Employee ID', 'Name', 'Total Salary']
    worksheet.append(headers)

    for entry in salary_sheet:
        row = [entry['employee'].employee_code, entry['employee'].name, entry['total_salary']]
        worksheet.append(row)

    excel_file = BytesIO()
    workbook.save(excel_file)
    excel_file.seek(0)

    response = HttpResponse(
        excel_file.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=salary_report.xlsx'

    return response



@login_required
def generate_pay_slip(request, employee_id): 
    employee = EmployeeModel.objects.get(id=employee_id)   
    envelope_size = (3.625 * 72, 5.5 * 72) # x 261 x 396

    employee = EmployeeModel.objects.get(id=employee_id)    

    if employee.gender == 'Male':
            prefix = 'Mr.'
            prefix2 = 'his'
    elif employee.gender == 'Female':
            prefix = 'Mrs.'
            prefix2 = 'her'
    else:
            prefix = '' 
            prefix2 =''
   
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pay_slip_{employee_id}.pdf"'
    
    pdf_canvas = canvas.Canvas(response, pagesize=envelope_size)   
    
    pdf_canvas.setFont("Helvetica", 10)
    pdf_canvas.setFillColor('blue')
    pdf_canvas.drawString(50, 360, f" Mymeplus Technology Limited")

    pdf_canvas.setFont("Helvetica-Bold", 10)
    pdf_canvas.setFillColor('black')
    pdf_canvas.drawString(50, 330, f"Date: {timezone.now().date()}")

    pdf_canvas.setFont("Helvetica", 10)
    pdf_canvas.drawString(50, 300, f"Employee Code: {employee.employee_code}")
    pdf_canvas.drawString(50, 280, f"Name: {employee.name}")
    pdf_canvas.drawString(50, 260, f"Position: {employee.position}")
    pdf_canvas.drawString(50, 240, f"Department: {employee.department}")
    pdf_canvas.drawString(50, 220, f"Employee Level: {employee.employe_level}")
    

    pdf_canvas.drawString(50, 200, f"Basic Salary: {employee.basic_salary}")
    pdf_canvas.drawString(50, 180, f"House Allowance: {employee.house_allowance}")
    pdf_canvas.drawString(50, 160, f"Medical Allowance: {employee.medical_allowance}")
    pdf_canvas.drawString(50, 140, f"Transportation Allowance: {employee.transportation_allowance}")
    
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(50, 110, f"Pay Slip for {prefix} {employee.first_name} {employee.last_name}")  

    pdf_canvas.setFont("Helvetica", 10)
    cfo_employee = EmployeeModel.objects.filter(position='CFO').first()
    if cfo_employee:
        pdf_canvas.drawString(50, 70, f"Autorized Signature________________")  
        pdf_canvas.drawString(80, 50, f"Name:{cfo_employee.name}")  
        pdf_canvas.drawString(80, 30, f"Designation:{cfo_employee.position}")  
    else:
        pdf_canvas.drawString(50, 70, f"Autorized Signature________________")  
        pdf_canvas.drawString(80, 50, f"Name:........") 
        pdf_canvas.drawString(80, 30, f"Designation:.....")  
       
    pdf_canvas.setFont("Helvetica-Bold", 7)
    pdf_canvas.setFillColor('green')
    pdf_canvas.drawString(30, 15, f"Signature is not required due to computerized authorization")  
    
    pdf_canvas.setFillColor('yellow') 
    pdf_canvas.rect(5, 5, 250,385)

    pdf_canvas.showPage()
    pdf_canvas.save()
    
    return response



@login_required
def generate_salary_certificate(request, employee_id):  
    a4_size = A4    
    employee = EmployeeModel.objects.get(id=employee_id)   

    if employee.gender == 'Male':
            prefix = 'Mr.'
            prefix2 = 'his'
    elif employee.gender == 'Female':
            prefix = 'Mrs.'
            prefix2 = 'her'
    else:
            prefix = '' 
            prefix2 =''
   
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="salary_certificate_{employee_id}.pdf"'
    
    pdf_canvas = canvas.Canvas(response, pagesize=a4_size)

    logo_path = os.path.join(settings.BASE_DIR, 'static/images/Logo.png')
  
    try:      
        logo = ImageReader(logo_path)
        pdf_canvas.drawImage(logo, 50, 750, width=50, height=50)
    except Exception as e: 
        print(f"Error loading logo image: {e}")
    
    spacing1 = 15
    y_space = 750
 
    pdf_canvas.setFont("Helvetica", 12) 
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "mymeplus Technology Limited")
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "House#39, Road#15, Block#F, Bashundhara R/A, Dhaka-1229")
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "Phone:01842800705")
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "email: hkobir@mymeplus.com")
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "website: www.mymeplus.com")


    current_date = datetime.now().strftime("%Y-%m-%d")
    pdf_canvas.drawString(50, 650, f"Date: {current_date}") 

    pdf_canvas.drawString(50, 620, f"Salary Certificate for {prefix} {employee.first_name} {employee.last_name}")

    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(200, 560, "To Whom It May Concern")
 
    
    pdf_canvas.setFont("Helvetica", 10)
    text_y = 500
    text_y2 = 470
    text_y3 = 400
    line_spacing = 15 
    
    pdf_canvas.drawString(50, text_y, f"This is to certify that {prefix} {employee.name} is working in the {employee.department} department since {employee.joining_date}, {prefix2} monthly")
    text_y -= line_spacing 
    pdf_canvas.drawString(50, text_y, f" remuneration is as follows:")
       
    pdf_canvas.drawString(150, text_y2, f"Basic Salary: {employee.basic_salary}")
    text_y2 -= line_spacing
    pdf_canvas.drawString(150, text_y2, f"House Allowance: {employee.house_allowance}")
    text_y2 -= line_spacing
    pdf_canvas.drawString(150, text_y2, f"Medical Allowance: {employee.medical_allowance}")
    text_y2 -= line_spacing
    pdf_canvas.drawString(150, text_y2, f"Transportation Allowance: {employee.transportation_allowance}")
    text_y2 -= line_spacing
    pdf_canvas.drawString(150, text_y2, f"Festival Bonus: {employee.bonus}")
    
    
    text_y3 -= line_spacing   
    pdf_canvas.drawString(50, text_y3, f"The total monthly remuneration of {employee.name} amounts to {employee.gross_monthly_salary}")
    text_y3 -= line_spacing
    pdf_canvas.drawString(50, text_y3, f"This certificate is issued upon request of {employee.name} for {prefix2} intended purpose. Please do not hesitate to contact us")
    text_y3 -= line_spacing
    pdf_canvas.drawString(50, text_y3, f"if further clarification is required.")

    pdf_canvas.drawString(50, 250, f"Sincerely,")


    cfo_employee = EmployeeModel.objects.filter(position='CFO').first()
    if cfo_employee:
        pdf_canvas.drawString(50, 150, f"Autorized Signature________________")  
        pdf_canvas.drawString(50, 135, f"Name:{cfo_employee.name}")  
        pdf_canvas.drawString(50, 120, f"Designation:{cfo_employee.position}")  
    else:
        pdf_canvas.drawString(50, 150, f"Autorized Signature________________")  
        pdf_canvas.drawString(50, 135, f"Name:........") 
        pdf_canvas.drawString(50, 120, f"Designation:.....")  

    pdf_canvas.setFont("Helvetica-Bold", 10)
    pdf_canvas.setFillColor('green')
    pdf_canvas.drawString(50,80, f"Signature is not mandatory due to computerized authorization")  
      
    pdf_canvas.showPage()
    pdf_canvas.save()
    
    return response




def generate_experience_certificate(request, employee_id):  
    a4_size = A4    
    employee = EmployeeModel.objects.get(id=employee_id)    
   
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="experience_certificate_{employee_id}.pdf"'
    
    pdf_canvas = canvas.Canvas(response, pagesize=a4_size)
    if employee.gender == 'Male':
            prefix = 'Mr.'
            prefix2 = 'his'
            prefix3 ='him'
    elif employee.gender == 'Female':
            prefix = 'Mrs.'
            prefix2 = 'her'
            prefix3 = 'her'
    else:
            prefix = '' 
            prefix2 =''
            prefix3 =''



    logo_path = os.path.join(settings.BASE_DIR, 'static/images/Logo.png')
  
    try:      
        logo = ImageReader(logo_path)
        pdf_canvas.drawImage(logo, 50, 750, width=50, height=50)
    except Exception as e: 
        print(f"Error loading logo image: {e}")
    
    spacing1 = 15
    y_space = 750
 
    pdf_canvas.setFont("Helvetica", 12) 
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "mymeplus Technology Limited")
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "House#39, Road#15, Block#F, Bashundhara R/A, Dhaka-1229")
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "Phone:01842800705")
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "email: hkobir@mymeplus.com")
    y_space -= spacing1
    pdf_canvas.drawString(50,  y_space, "website: www.mymeplus.com")





    pdf_canvas.setFont("Helvetica", 12)
    pdf_canvas.drawString(50, 570, f"Experience Certificate for {prefix} {employee.first_name} {employee.last_name}")
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    pdf_canvas.drawString(50, 535, f"Date: {current_date}")


    pdf_canvas.drawString(50, 500, f"This is to certify that {prefix} {employee.first_name}  {employee.last_name} was employed at from {employee.joining_date} to {employee.resignation_date}.")
    pdf_canvas.drawString(50, 485, f"During {prefix2} tenure, {employee.name} held the position of {employee.position} as {prefix2} last designation and performed {prefix2}")
    pdf_canvas.drawString(50, 470, f"duties with dedication and professionalism. We wish {prefix3} all the best for {prefix2} future endeavors.")
   
   
    cfo_employee = EmployeeModel.objects.filter(position='CFO').first()
    if cfo_employee:
        pdf_canvas.drawString(50, 350, f"Autorized Signature________________")  
        pdf_canvas.drawString(50, 335, f"Name:{cfo_employee.name}")  
        pdf_canvas.drawString(50, 320, f"Designation:{cfo_employee.position}")  
    else:
        pdf_canvas.drawString(50, 350, f"Autorized Signature________________")  
        pdf_canvas.drawString(50, 335, f"Name:........") 
        pdf_canvas.drawString(50, 320, f"Designation:.....")  

    pdf_canvas.setFont("Helvetica-Bold", 10)
    pdf_canvas.setFillColor('green')
    pdf_canvas.drawString(50,280, f"Signature is not mandatory due to computerized authorization")  
  
    pdf_canvas.showPage()
    pdf_canvas.save()
    
    return response


 
############## Resource data #################################################################

@login_required
def create_resource(request):
    if request.method == 'POST':
        form = CreateResurceForm(request.POST)
        if form.is_valid():
            form.save()         
            return redirect('employee:view_resource')
        else:
            print(form.errors)  
    else:
        form = CreateResurceForm()    
    return render(request, 'employee/resource/create_resource_form.html', {'form': form})



@login_required
def update_resource(request, resource_id):
    resource = get_object_or_404(Resource, id= resource_id)
    if request.method == 'POST':
        form = CreateResurceForm(request.POST,instance=resource)
        if form.is_valid():
            form.save()         
            return redirect('employee:view_resource')
        else:
            print(form.errors)  
    else:
        form = CreateResurceForm(instance=resource)    
    return render(request, 'employee/resource/update_resource.html', {'form': form})



def view_resource2(request): 
    resources = Resource.objects.all()
    return render(request, 'employee/resource/view_resource.html', {'resources': resources})





@login_required
def view_resource2(request):   
    region = None
    zone = None
    mp = None

    form = SummaryReportChartForm(request.GET or {'days': 20})
    resources = Resource.objects.all()

    if form.is_valid():       
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')        

        if region:
            resources = resources.filter(region=region)
        if zone:
            resources = resources.filter(zone=zone)
        if mp:
            resources = resources.filter(mp=mp)

    # Pagination logic
    resource_data = []
    page_obj = None
    resource_per_page = 10
    paginator = Paginator(resources, resource_per_page)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    for resource in page_obj:       
        resource_dict = {}
        resource_fields = Resource._meta.get_fields()
        for field in resource_fields:
            field_name = field.name
            field_value = getattr(resource, field_name)
            resource_dict[field_name] = field_value

        resource_data.append(resource_dict)

    # Exclude empty fields from the form
    cleared_form = SummaryReportChartForm() 
    return render(request, 'employee/resource/view_resource.html', {
        'resource_data': resource_data,
        'page_obj': page_obj,
        'form': form,       
        'region': region,
        'zone': zone,
        'mp': mp,
        'form': cleared_form
    })



@login_required
def view_resource2(request):   
    region = None
    zone = None
    mp = None

    form = SummaryReportChartForm(request.GET or {'days': 20})
    resources = Resource.objects.all()

    if form.is_valid():       
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')        

        if region:
            resources = resources.filter(region=region)
        if zone:
            resources = resources.filter(zone=zone)
        if mp:
            resources = resources.filter(mp=mp)

    # Subqueries for counting good and faulty PGs
    good_pg_subquery = AddPGInfo.objects.filter(
        region=OuterRef('region'),
        zone=OuterRef('zone'),
        PG_status='good'
    ).values('region').annotate(good_count=Count('id')).values('good_count')

    faulty_pg_subquery = AddPGInfo.objects.filter(
        region=OuterRef('region'),
        zone=OuterRef('zone'),
        PG_status='faulty'
    ).values('region').annotate(faulty_count=Count('id')).values('faulty_count')

    # Annotate resources with the counts of good and faulty PGs
    resources = resources.annotate(
        num_of_good_PG=Subquery(good_pg_subquery, output_field=FloatField()),
        num_of_faulty_PG=Subquery(faulty_pg_subquery, output_field=FloatField())
    )

    # Pagination logic
    resource_data = []
    page_obj = None
    resource_per_page = 10
    paginator = Paginator(resources, resource_per_page)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    for resource in page_obj:       
        resource_dict = {}
        resource_fields = Resource._meta.get_fields()
        for field in resource_fields:
            field_name = field.name
            field_value = getattr(resource, field_name)
            resource_dict[field_name] = field_value

        resource_data.append(resource_dict)

    # Exclude empty fields from the form
    cleared_form = SummaryReportChartForm() 
    return render(request, 'employee/resource/view_resource.html', {
        'resource_data': resource_data,
        'page_obj': page_obj,
        'form': form,       
        'region': region,
        'zone': zone,
        'mp': mp,
        'form': cleared_form
    })


@login_required
def view_resource(request):   
    region = None
    zone = None
    mp = None

    form = SummaryReportChartForm(request.GET or {'days': 20})
    resources = Resource.objects.all()

    if form.is_valid():       
        region = form.cleaned_data.get('region')
        zone = form.cleaned_data.get('zone')
        mp = form.cleaned_data.get('mp')        

        if region:
            resources = resources.filter(region=region)
        if zone:
            resources = resources.filter(zone=zone)
        if mp:
            resources = resources.filter(mp=mp)

    # Subqueries for counting good and faulty PGs
    good_pg_subquery = AddPGInfo.objects.filter(
        region=OuterRef('region'),
        zone=OuterRef('zone'),
        mp=OuterRef('mp'),
        PG_status='good'
    ).values('region').annotate(good_count=Count('id')).values('good_count')

    faulty_pg_subquery = AddPGInfo.objects.filter(
        region=OuterRef('region'),
        zone=OuterRef('zone'),
        mp=OuterRef('mp'),
        PG_status='faulty'
    ).values('region').annotate(faulty_count=Count('id')).values('faulty_count')

    # Annotate resources with the counts of good and faulty PGs
    resources = resources.annotate(
        dynamic_num_of_good_PG=Subquery(good_pg_subquery, output_field=FloatField()),
        dynamic_num_of_faulty_PG=Subquery(faulty_pg_subquery, output_field=FloatField())
    )

    resources = resources.annotate(
        total_PG_count=F('dynamic_num_of_good_PG') + F('dynamic_num_of_faulty_PG')
    )

    for resource in resources:
        if resource.total_PG_count and resource.dynamic_num_of_faulty_PG and resource.total_PG_count != 0:
            resource.faulty_PG_percentage = (resource.dynamic_num_of_faulty_PG / resource.total_PG_count) * 100
        else:
            resource.faulty_PG_percentage = 0

    # Pagination logic
    resource_data = []
    page_obj = None
    resource_per_page = 10
    paginator = Paginator(resources, resource_per_page)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    for resource in page_obj:       
        resource_dict = {}
        resource_fields = Resource._meta.get_fields()
        for field in resource_fields:
            field_name = field.name
            field_value = getattr(resource, field_name)
            resource_dict[field_name] = field_value

        # Add the dynamic good and faulty PG counts
        resource_dict['dynamic_num_of_good_PG'] = resource.dynamic_num_of_good_PG
        resource_dict['dynamic_num_of_faulty_PG'] = resource.dynamic_num_of_faulty_PG

        resource_data.append(resource_dict)

    # Exclude empty fields from the form
    cleared_form = SummaryReportChartForm() 
    return render(request, 'employee/resource/view_resource.html', {
        'resource_data': resource_data,
        'page_obj': page_obj,
        'form': form,       
        'region': region,
        'zone': zone,
        'mp': mp,
        'form': cleared_form
    })



@login_required
def view_resource_summary(request):
    grouped_summary_data = {}
    total_site_count = None
    total_KPI_site_count = None
    total_good_PG_count = None
    total_faulty_PG_count = None
    total_PG_ranar_count = None
    total_head_count = None

    # Aggregate overall counts
    data = Resource.objects.all().aggregate(
        total_site=Sum('total_site'),
        total_KPI_site=Sum('no_of_KPI_site'),
        total_PG_ranar=Sum(F('num_of_PGTL') + F('num_of_PGR')),
        total_head=Sum(F('num_of_PGTL') + F('num_of_PGR') + F('num_of_operational_executive') + F('num_of_admin_account_executive')
                       + F('num_of_PG_repair_technician') + F('num_of_DG_repair_technician') + F('num_of_manager'))
    )

    # Count total good and faulty PGs
    total_good_PG_count = AddPGInfo.objects.filter(PG_status='good').count()
    total_faulty_PG_count = AddPGInfo.objects.filter(PG_status='faulty').count()

    total_site_count = data.get('total_site', 0)
    total_KPI_site_count = data.get('total_KPI_site', 0)
    total_PG_ranar_count = data.get('total_PG_ranar', 0)
    total_head_count = data.get('total_head', 0)

    # Subqueries for counting good and faulty PGs
    good_pg_subquery = AddPGInfo.objects.filter(
        region=OuterRef('region'),
        zone=OuterRef('zone'),
        PG_status='good'
    ).values('region').annotate(good_count=Count('id')).values('good_count')

    faulty_pg_subquery = AddPGInfo.objects.filter(
        region=OuterRef('region'),
        zone=OuterRef('zone'),
        PG_status='faulty'
    ).values('region').annotate(faulty_count=Count('id')).values('faulty_count')

    # Aggregate summary data
    summary = Resource.objects.all() \
        .values('region', 'zone') \
        .annotate(
            total_site=Sum('total_site'),
            no_of_KPI_site=Sum('no_of_KPI_site'),
            num_of_PGTL=Sum('num_of_PGTL'),
            num_of_PGR=Sum('num_of_PGR'),
            num_of_adhoc_PGR=Sum('num_of_adhoc_PGR'),
            num_of_vehicle=Sum('num_of_vehicle'),
            num_of_adhoc_vehicle=Sum('num_of_adhoc_vehicle'),
            num_of_PG_repair_technician=Sum('num_of_PG_repair_technician'),
            num_of_DG_repair_technician=Sum('num_of_DG_repair_technician'),
            num_of_operational_executive=Sum('num_of_operational_executive'),
            num_of_admin_account_executive=Sum('num_of_admin_account_executive'),
            num_of_manager=Sum('num_of_manager'),
            num_of_other_staff=Sum('num_of_other_staff'),
            total_human_resource=Sum('total_human_resource'),
            # Use subqueries to count good and faulty PGs dynamically
            num_of_good_PG=Subquery(good_pg_subquery, output_field=FloatField()),
            num_of_faulty_PG=Subquery(faulty_pg_subquery, output_field=FloatField()),
            faulty_PG_percentage=ExpressionWrapper(
                (F('num_of_faulty_PG') * 100.0) / (F('num_of_faulty_PG') + F('num_of_good_PG')),
                output_field=FloatField()
            ),
            KPI_site_percentage=ExpressionWrapper(
                (F('no_of_KPI_site') * 100.0) / (F('total_site')),
                output_field=FloatField()
            )
        ) \
        .order_by('region', 'zone')

    for data in summary:
        region = data['region']
        if region not in grouped_summary_data:
            grouped_summary_data[region] = []
        grouped_summary_data[region].append(data)

    return render(request, 'employee/resource/resource_summary.html', {
        'grouped_summary_data': grouped_summary_data,
        'total_site': total_site_count,
        'total_KPI_site': total_KPI_site_count,
        'total_good_PG': total_good_PG_count,
        'total_faulty_PG': total_faulty_PG_count,
        'total_PG_ranar': total_PG_ranar_count,
        'total_head_count': total_head_count
    })
