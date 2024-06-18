
from django import forms
from account.models import Customer

from .models import MoneyRequisition, SummaryExpenses
from datetime import timedelta
from .models import DailyExpenseRequisition,SummaryExpenses,AdhocRequisition
from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES



class MoneyRequisitionForm(forms.ModelForm):
    class Meta:
        model = MoneyRequisition
        fields = ['region', 'zone','purpose', 'requisition_amount', 'supporting_documents']
 
    

class ApprovalForm(forms.ModelForm):
    class Meta:
        model = MoneyRequisition
        fields = [] 

    def __init__(self, *args, **kwargs):
        user_level = kwargs.pop('user_level', None)
        super(ApprovalForm, self).__init__(*args, **kwargs)
        if user_level == 'level1':
            self.fields['level1_approval_status'] = forms.ChoiceField(choices=MoneyRequisition.APPROVAL_STATUS_CHOICES)
            self.fields['level1_comments'] = forms.TextField()
        elif user_level == 'level2':
            self.fields['level2_approval_status'] = forms.ChoiceField(choices=MoneyRequisition.APPROVAL_STATUS_CHOICES)
            self.fields['level2_comments'] = forms.TextField()
        elif user_level == 'level3':
            self.fields['level3_approval_status'] = forms.ChoiceField(choices=MoneyRequisition.APPROVAL_STATUS_CHOICES)
            self.fields['level3_comments'] = forms.TextField()



class MoneySendingForm(forms.ModelForm):   
    TakePicture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'accept': 'image/*', 'capture': 'camera'}))  # File input field with 'capture' attribute for camera capture
    UploadPicture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}))  # File input field without 'capture' attribute for file selection  
  
    class Meta:
        model =  MoneyRequisition
        fields = ['money_sending_date']      
        widgets = {
                'money_sending_date': forms.TimeInput(attrs={'type': 'date'})          
            
                     }
        
    def clean(self):
        cleaned_data = super().clean()
        upload_picture = cleaned_data.get('UploadPicture')
        take_picture = cleaned_data.get('TakePicture')

        if upload_picture and take_picture:
            raise forms.ValidationError("Please choose either Upload Picture or Take Picture, not both.")

        return cleaned_data
    


class SummaryExpensesForm(forms.ModelForm):
    total_run_hour = forms.FloatField(label='Total Run Hour (hours with decimals)', required=False)

    class Meta:
        model = SummaryExpenses
        fields = [
            'region',
            'zone',
            'total_amount_received',
            'office_expenses',
            'local_expenses',
            'on_demand_vehicle_cost',
            'adhoc_PGR_cost',
            'dgow_vehicle_cost',
            'dgow_run_fuel_cost_cash',
            'pm_vehicle_fuel_cost_cash',
            'cm_vehicle_fuel_cost_cash',
            'pgrun_fuel_cost_cash',
            'pgrun_fuel_cost_pump',
            'site_pm_cost',
            'optima_billable',
            'optima_non_billable',
            'office_rent',
            'others',
            'advance_due',
            'total_tt',
            'total_run_hour',
            'updated_at'
          
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.total_run_hour is not None:
            # Calculate total run hours correctly
            total_run_hours = self.instance.total_run_hour.total_seconds() / 3600.0  # Convert timedelta to hours as float
            self.fields['total_run_hour'].initial = total_run_hours
            print(f"DEBUG: Initialized total_run_hour: {total_run_hours}")  # Debug statement

    def clean_total_run_hour(self):
        """Convert the inputted total_run_hour from hours with decimals to timedelta."""
        total_run_hour = self.cleaned_data.get('total_run_hour')
        if total_run_hour is not None:
            total_run_hour_duration = timedelta(hours=total_run_hour)
            print(f"DEBUG: Cleaned total_run_hour (timedelta): {total_run_hour_duration}")  # Debug statement
            return total_run_hour_duration
        return None  # Handle case where total_run_hour is not provided

    def save(self, commit=True):
        instance = super().save(commit=False)
        total_run_hour = self.cleaned_data.get('total_run_hour')
        if total_run_hour is not None:
            instance.total_run_hour = total_run_hour
            print(f"DEBUG: Saved total_run_hour (timedelta): {total_run_hour}") 
        if commit:
            instance.save()
        return instance





class ZoneWiseExpensesForm(forms.Form):   
    zone = forms.ChoiceField(choices=ZONE_CHOICES,required=False)   
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)



class ExpenseRequisitionForm(forms.ModelForm):
    class Meta:
        model = DailyExpenseRequisition
        fields = ['region', 'zone','mp','purpose','pgnumber','vehicle', 'requisition_amount','from_address','to_address','mode_travel','supporting_documents','description']
 
 
   



class ExpenseRequisitionStatusForm(forms.Form):
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
    region = forms.ChoiceField(
        label='Select Region',
        required=False,
        choices=REGION_CHOICES
    )
    zone = forms.ChoiceField(
        label='Select Zone',
        required=False,
        choices=ZONE_CHOICES
    )
    mp = forms.ChoiceField(
        label='Select MP',
        required=False,
        choices=MP_CHOICES
    )

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     # Fetching data from the models to populate choices
    #     self.fields['region'].choices = [('', '------')] + [(region.id, region.name) for region in Region.objects.all()]
    #     self.fields['zone'].choices = [('', '------')] + [(zone.id, zone.name) for zone in Zone.objects.all()]
    #     self.fields['mp'].choices = [('', '------')] + [(mp.id, mp.name) for mp in MP.objects.all()]




class AdhocRequisitionForm(forms.ModelForm):
    class Meta:
        model = AdhocRequisition
        fields = ['region', 'zone','no_of_adhoc_man_day','no_of_adhoc_vehicle_day','purpose', 'requisition_amount', 'supporting_documents']
 





class AdhocRequisitionStatusForm(forms.Form):
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
    region = forms.ChoiceField(
        label='Select Region',
        required=False,
        choices=REGION_CHOICES
    )
    zone = forms.ChoiceField(
        label='Select Zone',
        required=False,
        choices=ZONE_CHOICES
    )
    mp = forms.ChoiceField(
        label='Select MP',
        required=False,
        choices=MP_CHOICES

    )

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     # Fetching data from the models to populate choices
    #     self.fields['region'].choices = [('', '------')] + [(region.id, region.name) for region in Region.objects.all()]
    #     self.fields['zone'].choices = [('', '------')] + [(zone.id, zone.name) for zone in Zone.objects.all()]
    #     self.fields['mp'].choices = [('', '------')] + [(mp.id, mp.name) for mp in MP.objects.all()]





class dailyExpenseSummaryForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    days = forms.IntegerField(required=False)
    region = forms.ChoiceField(choices=REGION_CHOICES,required=False)
    zone = forms.ChoiceField(choices=ZONE_CHOICES,required=False)
    mp = forms.ChoiceField(choices=MP_CHOICES,required=False)
