
from django import forms
from account.models import Customer
from datetime import timedelta
from .models import AddVehicleInfo,VehicleRuniningData,FuelRefill
from .models import VehicleRentalCost,Vehiclefault

from common.models import Region,Zone,MP
from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES



class AdVehicleForm(forms.ModelForm):
    vehicle_joining_date = forms.DateField(label='vehicle_joining_date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
         
    class Meta:
        model = AddVehicleInfo
        exclude = ['vehicle_id','vehicle_add_requester','created_at','vehicle_cancel_date'] 
 
   
class AddVehicleExpensesForm(forms.ModelForm):
    start_time = forms.DateTimeField(label='Start Time', required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    stop_time = forms.DateTimeField(label='Stop Time', required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = VehicleRuniningData
        exclude = ['fuel_refill', 'total_fuel_cost', 'vehicle_expense_id',
                   'vehicle_expense_add_requester', 'total_kilometer_run',
                   'Vehicle_fuel_balance', 'total_fuel_consumed',
                   'created_at', 'travel_date', 'running_hours',
                   'overtime_hours', 'overtime_cost', 'fuel_balance', 'comments']

        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['region'].queryset = Region.objects.all()
        self.fields['zone'].queryset = Zone.objects.all()
        self.fields['mp'].queryset = MP.objects.all()


   
   
class FuelRefillForm(forms.ModelForm):   
    refill_date = forms.DateField(label='refill_date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = FuelRefill
        exclude = ['fuel_refill_code','vehicle_total_fuel_reserve','refill_requester',
                   'vehicle_kilometer_run','vehicle_fuel_consumed',
                   'vehicle_fuel_balance','created_at','refill_date'
                   ] 
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
        }


    def clean_refill_date(self):
        refill_date = self.cleaned_data['refill_date']
        if not refill_date:
            raise forms.ValidationError("Refill date is required.")
        return refill_date
  
  

class UpdateVehicleDatabaeForm(forms.ModelForm):
    vehicle_joining_date = forms.DateField(label='vehicle_joining_date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    vehicle_cancel_date = forms.DateField(label='vehicle_cancel_date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = AddVehicleInfo
        exclude = ['vehicle_id',' vehicle_add_requester'] 

    def __init__(self, *args, **kwargs): 
        user_role = kwargs.pop('user_role', None)
        super().__init__(*args, **kwargs)        
       
        # if user_role == 'external':
        #     self.fields['hepta_generator_start_time'].widget = forms.HiddenInput()
        #     self.fields['hepta_generator_stop_time'].widget = forms.HiddenInput()
     

class vehicleSummaryReportForm(forms.Form):
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
        required=False
    )
    zone = forms.ChoiceField(
        label='Select Zone',
        required=False
    )
    mp = forms.ChoiceField(
        label='Select MP',
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fetching data from the models to populate choices
        self.fields['region'].choices = [('', '------')] + [(region.id, region.name) for region in Region.objects.all()]
        self.fields['zone'].choices = [('', '------')] + [(zone.id, zone.name) for zone in Zone.objects.all()]
        self.fields['mp'].choices = [('', '------')] + [(mp.id, mp.name) for mp in MP.objects.all()]

        # Debugging: Print choices to verify
        print("Region choices:", self.fields['region'].choices)
        print("Zone choices:", self.fields['zone'].choices)
        print("MP choices:", self.fields['mp'].choices)


   
class VehicleDetailsForm(forms.Form):   
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



class VehicleDatabaseViewForm(forms.Form): 
    vehicle_reg_number = forms.CharField(label='Vehicle Registration Number', required=False)  # Add this field
    region = forms.ChoiceField(choices=REGION_CHOICES, required=False)
    zone = forms.ChoiceField(choices=ZONE_CHOICES, required=False)
    mp = forms.ChoiceField(choices=MP_CHOICES, required=False)
    class Meta:
        model = AddVehicleInfo
        fields = ['region',' zone','mp','vehicle_reg_number'] 


class RentalPeriodForm(forms.Form):
    start_date = forms.DateField(label='Start date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='End date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))



class VehiclePaymentForm(forms.ModelForm):   
    class Meta:
        model = VehicleRentalCost
        fields = ['region', 'zone', 'mp', 'vehicle', 'vehicle_rent_paid', 'vehicle_body_overtime_paid', 'vehicle_driver_overtime_paid']



class VehicleFaulttForm(forms.ModelForm):
    fault_start_time = forms.DateTimeField(label='Fault Time', required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    fault_stop_time = forms.DateTimeField(label='Fault End Time', required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
   
   
    class Meta:
        model = Vehiclefault
        fields = ['region', 'zone', 'mp', 'vehicle', 'fault_start_time','fault_stop_time','fault_type','fault_location']







class vehicleSummaryReportForm(forms.Form):
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
        required=False
    )
    zone = forms.ChoiceField(
        label='Select Zone',
        required=False
    )
    mp = forms.ChoiceField(
        label='Select MP',
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fetching data from the models to populate choices
        self.fields['region'].choices = [('', '------')] + [(region.id, region.name) for region in Region.objects.all()]
        self.fields['zone'].choices = [('', '------')] + [(zone.id, zone.name) for zone in Zone.objects.all()]
        self.fields['mp'].choices = [('', '------')] + [(mp.id, mp.name) for mp in MP.objects.all()]
