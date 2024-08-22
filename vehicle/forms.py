
from django import forms
from account.models import Customer
from datetime import timedelta
from .models import AddVehicleInfo,VehicleRuniningData,FuelRefill
from .models import VehicleRentalCost,Vehiclefault
from django.core.exceptions import ValidationError

from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES
from datetime import datetime


class AdVehicleForm(forms.ModelForm):
    vehicle_joining_date = forms.DateField(label='vehicle_joining_date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
         
    class Meta:
        model = AddVehicleInfo
        exclude = ['vehicle_id','vehicle_add_requester','created_at','vehicle_cancel_date'] 
 
   
class AddVehicleExpensesForm(forms.ModelForm):
    start_time = forms.DateTimeField(label='Start Time', required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    stop_time = forms.DateTimeField(label='Stop Time', required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    travel_date = forms.DateField(label='Travel date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = VehicleRuniningData
        exclude = ['fuel_refill', 'total_fuel_cost', 'vehicle_expense_id',
                   'vehicle_expense_add_requester', 'total_kilometer_run',
                   'Vehicle_fuel_balance', 'total_fuel_consumed',
                   'created_at', 'running_hours',
                   'overtime_hours', 'overtime_cost','fuel_balance', 'comments',
                   'day_end_kilometer_cost_CNG','day_end_kilometer_cost_gasoline','total_kilometer_cost','day_end_kilometer_run']

        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
        }
     
   
class FuelRefillForm(forms.ModelForm):   
    refill_date = forms.DateField(label='refill_date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = FuelRefill
        exclude = ['fuel_refill_code','vehicle_total_fuel_reserve','refill_requester',
                   'vehicle_kilometer_run','vehicle_fuel_consumed',
                   'vehicle_fuel_balance','created_at','refill_date','fuel_cost'
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
        super(UpdateVehicleDatabaeForm, self).__init__(*args, **kwargs)      
        if user_role == 'general_user':
            for field in self.fields.values():
                field.widget.attrs['readonly'] = True
           

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
        fields = ['region', 'zone', 'mp', 'vehicle', 'vehicle_rent_paid','vehicle_body_overtime_paid']



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

    vehicle_number = forms.CharField(
        label='Vehicle Number',
        required=False,
     
    )
    
    pg_number = forms.CharField(
        label='PG Number',
        required=False,
     
    )



######### adhoc vehicle only management mechanism ########################
   
from.models import AdhocVehicleAttendance,AdhocVehiclePayment,AdhocVehicleRequisition

class AdhocRequisitionForm(forms.ModelForm):
    class Meta: 
        model = AdhocVehicleRequisition
        fields = ['vehicle','start_date','end_date','purpose']

        widgets = {
                'start_date': forms.TimeInput(attrs={'type': 'date'}),
                'end_date': forms.TimeInput(attrs={'type': 'date'}),
                           
                     }



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

    vehicle = forms.CharField(
        label='Vehicle',
        required=False,
        
    )

class AdhocAttendanceIntimeForm(forms.ModelForm):
    class Meta:
        model = AdhocVehicleAttendance
        fields = ['vehicle', 'adhoc_in_date', 'adhoc_in_time','adhoc_requisition']
        widgets = {
            'adhoc_in_date': forms.DateInput(attrs={'type': 'date'}),
            'adhoc_in_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        vehicle = cleaned_data.get('vehicle') 
        adhoc_in_date = cleaned_data.get('adhoc_in_date')
        adhoc_in_time = cleaned_data.get('adhoc_in_time')

        if vehicle and adhoc_in_date and adhoc_in_time:
            requisitions = AdhocVehicleRequisition.objects.filter(
                vehicle=vehicle,
                active_status=True,
                start_date__lte=adhoc_in_date,
                end_date__gte=adhoc_in_date,
                level1_approval_status='Approved'
            )

            if not requisitions.exists():
                raise ValidationError("This adhoc has no active approval.")
            
            # Selecting the first requisition if multiple are found
            requisition = requisitions.first()

            if not (requisition.start_date <= adhoc_in_date <= requisition.end_date):
                raise ValidationError("In-date must be within the requisition's start and end dates.")

            existing_attendance = AdhocVehicleAttendance.objects.filter(
                vehicle=vehicle,
                adhoc_in_date=adhoc_in_date,
                adhoc_in_time=adhoc_in_time
            ).exclude(id=self.instance.id)
            if existing_attendance.exists():
                raise ValidationError("In-date and in-time can be given only once within the same start-date and end-date.")

        return cleaned_data

                                


class AdhocAttendanceUpdateOuttimeForm(forms.ModelForm):
    class Meta:
        model = AdhocVehicleAttendance
        fields = ['vehicle', 'adhoc_out_date', 'adhoc_out_time']
        widgets = {
            'adhoc_out_date': forms.DateInput(attrs={'type': 'date'}),
            'adhoc_out_time': forms.TimeInput(attrs={'type': 'time'})
        }

    def clean(self):
        cleaned_data = super().clean()
        vehicle = self.instance.vehicle
        adhoc_in_date = self.instance.adhoc_in_date
        adhoc_in_time = self.instance.adhoc_in_time
        adhoc_out_date = cleaned_data.get('adhoc_out_date')
        adhoc_out_time = cleaned_data.get('adhoc_out_time')

        if adhoc_out_date and adhoc_out_time:
            requisition = self.instance.get_active_requisition()
            if requisition:
                if not (requisition.start_date <= adhoc_out_date <= requisition.end_date):
                    raise ValidationError("Out-date must be within the requisition's start and end dates.")

                existing_out_time = AdhocVehicleAttendance.objects.filter(
                    vehicle=vehicle,
                    adhoc_out_date=adhoc_out_date,
                    adhoc_out_time=adhoc_out_time
                ).exclude(id=self.instance.id)
                if existing_out_time.exists():
                    raise ValidationError("Out-time can be given only once within the same start-date and end-date.")

                in_datetime = datetime.combine(adhoc_in_date, adhoc_in_time)
                out_datetime = datetime.combine(adhoc_out_date, adhoc_out_time)
                self.instance.adhoc_working_hours = (out_datetime - in_datetime).total_seconds() / 3600

        return cleaned_data

                     



class AdhocPaymentForm(forms.ModelForm):
    class Meta:
        model = AdhocVehiclePayment
        exclude=['payment_id','created_at']

      


class AdhocVehiclePaymentFormCommon(forms.ModelForm):   
    class Meta:
        model = AdhocVehiclePayment
        fields = ['vehicle', 'adhoc_paid_amount','payment_mode','transaction_id','payment_supporting_document']

