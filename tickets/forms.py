from django import forms
from .models import eTicket,ChatMessage,ChildTicket
from .mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES
from .models import ChildTicketExternal

from generator.models import AddPGInfo
from .models import eTicket,Region, Zone, MP, PGRdatabase
from vehicle.models import AddVehicleInfo


class ChatForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'placeholder': 'Enter your message here...'})
        }


class CreateTicketFormEdotco(forms.ModelForm):
    class Meta:
        model =  eTicket
        fields = ['region', 'zone', 'mp', 'site_id','customer_ticket_ref','customer_name']
   
    # region = forms.ChoiceField(choices=REGION_CHOICES)
    # zone = forms.ChoiceField(choices=ZONE_CHOICES)
    # mp = forms.ChoiceField(choices=MP_CHOICES)


class UpdateTicketFormEdotco(forms.ModelForm):
    TICKET_STATUS_CHOICES = [
        ('open', 'open'),
        ('running', 'running'),
        ('onTheWay', 'onTheWay'),
        ('TT_Miss', 'TT_Miss'),
        ('TT_Valid', 'TT_Valid'),
        ('TT_connected', 'TT_connected'),
        ('team_assign', 'team_assign'),
        ('TT_invalid', 'TT_invalid'),
    ]

    ASSIGNED_PG_RUNNER_CHOICES = [
        ('Permanent', 'Permanent'),
        ('Adhoc', 'Adhoc'),
    ]

    VEHICLE_TYPE_CHOICES = [
        ('Permanent', 'Permanent'),
        ('Adhoc', 'Adhoc'),
    ]

    assigned_pg_runner_type = forms.ChoiceField(choices=ASSIGNED_PG_RUNNER_CHOICES, required=False)
    assigned_vehicle_type = forms.ChoiceField(choices=VEHICLE_TYPE_CHOICES, required=False)
    ticket_status = forms.ChoiceField(choices=TICKET_STATUS_CHOICES, label='Ticket Status')
    vehicle = forms.ModelChoiceField(queryset=AddVehicleInfo.objects.all(), required=False)
    pgnumber = forms.ModelChoiceField(queryset=AddPGInfo.objects.all(), required=False)

    class Meta:
        model = eTicket
        fields = [
            'assigned_to', 'assigned_pg_runner_type','team_leader_name', 'vehicle', 'assigned_vehicle_type', 'pgnumber', 'ticket_status'
        ]

    def __init__(self, *args, **kwargs):
        user_role = kwargs.pop('user_role', None)
        super().__init__(*args, **kwargs)

        if user_role == 'external':
            self.fields['internal_generator_start_time'].widget = forms.HiddenInput()
            self.fields['internal_generator_stop_time'].widget = forms.HiddenInput()

     



# this form actually will be used for PG start time input only. for TT stop time- ajax function will be used. no
# form for PG stop is needed as ajax can update stop time directly
class CreateChildTicketForm(forms.ModelForm):
    parent_ticket_number = forms.CharField(max_length=50, label='Parent Ticket Number', required=True, widget=forms.TextInput(attrs={'readonly': 'readonly'}))   
    TakePicture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'accept': 'image/*', 'capture': 'camera'}))  # File input field with 'capture' attribute for camera capture
    UploadPicture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}))  # File input field without 'capture' attribute for file selection  
  
    class Meta:
        model =  ChildTicket
        fields = ['parent_ticket_number','child_internal_generator_start_time']      
        widgets = {
                'child_internal_generator_start_time': forms.TimeInput(attrs={'type': 'time'})          
            
                     }
        
    def clean(self):
        cleaned_data = super().clean()
        upload_picture = cleaned_data.get('UploadPicture')
        take_picture = cleaned_data.get('TakePicture')

        if upload_picture and take_picture:
            raise forms.ValidationError("Please choose either Upload Picture or Take Picture, not both.")

        return cleaned_data
    


class TicketStatusUpdateForm(forms.ModelForm):
    internal_ticket_number = forms.CharField(max_length=50, label='Parent Ticket Number', required=True, widget=forms.TextInput(attrs={'readonly': 'readonly'}))   
   
    class Meta:
        model =  eTicket
        fields = ['internal_ticket_number','ticket_status']      
      
class DateFormEdotco(forms.ModelForm):
    report_date = forms.DateField(label='Report Date', widget=forms.DateInput(attrs={'type': 'date'}))



class SummaryReportForm(forms.Form):
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




class MPReportForm(forms.Form):
    mp = forms.ChoiceField(label='Select MP', choices=MP_CHOICES, required=True)
    days = forms.IntegerField(label='Number of Days', min_value=1, required=False)
    start_date = forms.DateField(label='Start Date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='End Date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    def clean(self):
        cleaned_data = super().clean()
        days = cleaned_data.get('days')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
   
        if days and (start_date or end_date):
            raise forms.ValidationError("You can't specify both a date range and number of days.")
      
        if start_date and not end_date:
            raise forms.ValidationError("Both start and end dates must be provided for a date range.")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date must be later than start date.")

        return cleaned_data




class ZoneReportForm(forms.Form):
    zone = forms.ChoiceField(label='Select Zone', choices=ZONE_CHOICES, required=True)
    days = forms.IntegerField(label='Number of Days', min_value=1, required=False)
    start_date = forms.DateField(label='Start Date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='End Date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    def clean(self):
        cleaned_data = super().clean()
        days = cleaned_data.get('days')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')   
   
        if days and (start_date or end_date):
            raise forms.ValidationError("You can't specify both a date range and number of days.")
      
        if start_date and not end_date:
            raise forms.ValidationError("Both start and end dates must be provided for a date range.")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date must be later than start date.")

        return cleaned_data




class SummaryReportFormHourly(forms.Form):
    hours = forms.IntegerField(label='Number of hours', required=True, min_value=1)





class SummaryReportChartForm(forms.Form):
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
        label ='Select Region',
        required = False,
        choices=[('', '------')] + REGION_CHOICES

    )

    zone = forms.ChoiceField(
        label ='Select zone',
        required = False,
        choices=[('', '------')] + ZONE_CHOICES

    )

    mp = forms.ChoiceField(
        label ='Select MP',
        required = False,
       choices=[('', '------')] + MP_CHOICES

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




class PGRForm(forms.ModelForm):
    TakePicture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'accept': 'image/*', 'capture': 'camera'})) 
    UploadPicture = forms.ImageField(required=False,widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}))  
    joining_date = forms.DateField(label='joining_date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = PGRdatabase
        fields = [
            'region', 'zone', 'mp', 'name','PGR_type', 'PGR_category','phone', 'email',
            'address','joining_date','reference_person_name','reference_person_phone', 'PGR_birth_certificate'
        ]

    def clean(self):
        cleaned_data = super().clean()
        upload_picture = cleaned_data.get('UploadPicture')
        take_picture = cleaned_data.get('TakePicture')

        if upload_picture and take_picture:
            raise forms.ValidationError("Please choose either Upload Picture or Take Picture, not both.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        upload_picture = self.cleaned_data.get('UploadPicture')
        take_picture = self.cleaned_data.get('TakePicture')

        if take_picture:
            instance.PGR_photo = take_picture
        elif upload_picture:
            instance.PGR_photo = upload_picture

        if commit:
            instance.save()

        return instance
    



class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()
