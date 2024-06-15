from django import forms
from .models import EmployeeModel,AttendanceModel,Resource





class AddEmployeeForm(forms.ModelForm):
    joining_date = forms.DateField(label='joining_date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = EmployeeModel
        exclude = ['bonus','gross_monthly_salary','house_allowance','medical_allowance','transportation_allowance','updated_at'] 
 


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = AttendanceModel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)      
        self.fields['date'].widget = forms.DateInput(attrs={'type':'date'})   
        self.fields['check_in_time'].widget = forms.TimeInput(attrs={'type':'time'})   
        self.fields['check_out_time'].widget = forms.TimeInput(attrs={'type':'time'})   
        


class EditAttendanceForm(forms.ModelForm):
    class Meta:
        model = AttendanceModel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)      
        self.fields['date'].widget = forms.DateInput(attrs={'type':'date'})   
        self.fields['check_in_time'].widget = forms.TimeInput(attrs={'type':'time'})   
        self.fields['check_out_time'].widget = forms.TimeInput(attrs={'type':'time'})   
        


class MonthYearForm(forms.Form):
    month = forms.IntegerField(min_value=1, max_value=12)
    year = forms.IntegerField(min_value=2000, max_value=2700)



class CreateResurceForm(forms.ModelForm):    
    class Meta:
        model = Resource
        exclude = ['created_at','faulty_PG_percentage','total_human_resource','num_of_PGR','num_of_PGTL','num_of_vehicle','num_of_good_PG','num_of_faulty_PG'] 
 


class Resource_SummaryForm(forms.Form):
    report_date = forms.DateField(
        label='Report Date',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    days = forms.IntegerField(
        label='Number of Days',
        min_value=1,
        required=False
    )
