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
   
 


class CreateTicketFormEdotco2(forms.ModelForm):
    class Meta:
        model = eTicket
        fields = ['region', 'zone', 'mp', 'site_id', 'customer_ticket_ref', 'customer_name']
        widgets = {
            'region': forms.Select(attrs={'class': 'form-control', 'id': 'id_region'}),
            'zone': forms.Select(attrs={'class': 'form-control', 'id': 'id_zone'}),
            'mp': forms.Select(attrs={'class': 'form-control', 'id': 'id_mp'}),
        }





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



class SummaryReportForm2(forms.Form):
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
from common.models import Region, Zone, MP
from.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES
class SummaryReportForm(forms.Form):
    report_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    days = forms.IntegerField(required=False)
    region = forms.ModelChoiceField(queryset=Region.objects.all(), required=False)
    zone = forms.ModelChoiceField(queryset=Zone.objects.all(), required=False)
    mp = forms.ModelChoiceField(queryset=MP.objects.all(), required=False)
    # region = forms.ChoiceField(choices=REGION_CHOICES, required=False)
    # zone = forms.ChoiceField(choices=ZONE_CHOICES, required=False)
    # mp = forms.ChoiceField(choices=MP_CHOICES, required=False)





class MPReportForm(forms.Form):
     start_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
     end_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
     days = forms.IntegerField(required=False)     
     mp = forms.ModelChoiceField(queryset=MP.objects.all(), required=False)





class ZoneReportForm(forms.Form):
     start_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
     end_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
     days = forms.IntegerField(required=False)     
     zone = forms.ModelChoiceField(queryset=Zone.objects.all(), required=False)




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

    region = forms.ChoiceField(choices=REGION_CHOICES, required=False)
    zone = forms.ChoiceField(choices=ZONE_CHOICES, required=False)
    mp = forms.ChoiceField(choices=MP_CHOICES, required=False)
    # region = forms.ModelChoiceField(queryset=Region.objects.all(), required=False)
    # zone = forms.ModelChoiceField(queryset=Zone.objects.all(), required=False)
    # mp = forms.ModelChoiceField(queryset=MP.objects.all(), required=False)