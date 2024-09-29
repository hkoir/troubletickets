from django import forms
from.models import AddPGInfo,PGFaultRecord,PGFuelRefill
from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES


class AddPgForm(forms.ModelForm):
    PG_purchase_date = forms.DateField(label='PG_purchase_date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    PG_hire_date  = forms.DateField(label='PG_hire_date ', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = AddPGInfo
        exclude = ['PG_add_requester','created_at','updated_at','PG_code'] 
 

class UpdatePgDataBaseForm(forms.ModelForm):
    PG_purchase_date = forms.DateField(label='PG_purchase_date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    PG_hire_date  = forms.DateField(label='PG_hire_date ', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = AddPGInfo
        exclude = ['PG_add_requester','created_at','PG_code'] 
 
 
class UpdatePgStatusForm(forms.ModelForm):   
    class Meta:
        model = AddPGInfo
        fields = ['PG_status'] 
 


class PGDatabaseViewForm(forms.Form):   
    region = forms.ChoiceField(choices=REGION_CHOICES, required=False)
    zone = forms.ChoiceField(choices=ZONE_CHOICES, required=False)
    mp = forms.ChoiceField(choices=MP_CHOICES, required=False)
    PGNumber = forms.CharField(required=False)
   
   
from django import forms
from .models import PGFuelRefill, FuelPumpDatabase, AddPGInfo

from django import forms
from .models import PGFuelRefill, FuelPumpDatabase, AddPGInfo

class PGFuelRefillForm(forms.ModelForm):
    refill_date = forms.DateField(label='Refill date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    pgnumber = forms.ModelChoiceField(queryset=AddPGInfo.objects.all(), required=False, label='PG Number', widget=forms.Select(attrs={'class': 'form-control'}))
    fuel_pump = forms.ModelChoiceField(queryset=FuelPumpDatabase.objects.all(), required=False, label='Fuel Pump', widget=forms.Select(attrs={'class': 'form-control'}))
   

    class Meta:
        model = PGFuelRefill
        exclude = ['fuel_refill_code', 'refill_requester', 'fuel_cost', 'created_at']

    def clean_refill_date(self):
        refill_date = self.cleaned_data['refill_date']
        if not refill_date:
            raise forms.ValidationError("Refill date is required.")
        return refill_date



class PGFaultRecordForm(forms.ModelForm):   
    fault_date = forms.DateField(label='Fault date', required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = PGFaultRecord
        exclude=['created_at','updated_at','repair_date','repair_by','repair_cost','fault_duration','fault_type','action_taken']              
       
        widgets = {
            'pgnumber': forms.Select(attrs={'class': 'form-control'}),
        }


    def clean_fault_date(self):
        fault_date = self.cleaned_data['fault_date']
        if not fault_date:
            raise forms.ValidationError("fault_date date is required.")
        return fault_date
  
  
  
class UpdatePGFaultRecordForm(forms.ModelForm):   
    repair_date = forms.DateField(label='Reapir date', required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = PGFaultRecord
        exclude=['created_at','fault_date','updated_at','region','zone','mp','fault_duration']              
       
        widgets = {
            'pgnumber': forms.Select(attrs={'class': 'form-control'}),
        }


    def clean_repair_date(self):
        refill_date = self.cleaned_data['repair_date']
        if not refill_date:
            raise forms.ValidationError("repair date is required.")
        return refill_date
  
  
class PGNumberForm(forms.Form):
    pg_number = forms.CharField(label='PG Number', max_length=50,required=False)






class PgDetailsForm(forms.Form):   
    start_date = forms.DateField(
        label='Start Date',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    end_date = forms.DateField(
        label='End Date',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    days = forms.IntegerField(
        label='Number of Days',
        min_value=1,
        required=False
    )
  
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        days = cleaned_data.get('days')    

        if start_date and end_date and days:
            raise forms.ValidationError('Please specify either a date range or the number of days, but not both.')
        
        if (start_date and not end_date) or (end_date and not start_date):
            raise forms.ValidationError('Both start and end dates must be specified if you choose date range.')
        
        if not (start_date or end_date or days):
            raise forms.ValidationError('Please specify a date range or number of days for the report.')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError('Start date must be earlier than end date.')

        return cleaned_data





from.models import GeneratorService

class GeneratorServiceForm(forms.ModelForm):   
    date_of_service = forms.DateField(label='Date of service', required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = GeneratorService
        exclude=['created_at','service_requester']              
       
        widgets = {
            'pgnumber': forms.Select(attrs={'class': 'form-control'}),
        }


    def clean_repair_date(self):
        date_of_service = self.cleaned_data['date_of_service']
        if not  date_of_service:
            raise forms.ValidationError("date of service is required.")
        return  date_of_service
  