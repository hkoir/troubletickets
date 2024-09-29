from django import forms
from common.models import PGRdatabase
from .models import AdhocManRequisition,AdhocAttendance,AdhocPayment
from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES

from django.core.exceptions import ValidationError
from datetime import datetime



class AdhocRequisitionForm(forms.ModelForm):
    class Meta: 
        model = AdhocManRequisition
        fields = ['pgr','start_date','end_date','purpose']

        widgets = {
                'start_date': forms.DateInput(attrs={'type': 'date'}),
                'end_date': forms.DateInput(attrs={'type': 'date'}),
                           
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

    pgr=forms.CharField(required=False)


class AdhocAttendanceIntimeForm(forms.ModelForm):
    class Meta:
        model = AdhocAttendance
        fields = ['pgr', 'adhoc_requisition', 'adhoc_ticket', 'adhoc_in_date', 'adhoc_in_time']
        widgets = {
            'adhoc_in_date': forms.DateInput(attrs={'type': 'date'}),
            'adhoc_in_time': forms.TimeInput(attrs={'type': 'time'})
        }




class AdhocAttendanceIntimeForm(forms.ModelForm):
    class Meta:
        model = AdhocAttendance
        fields = ['pgr', 'adhoc_requisition', 'adhoc_ticket', 'adhoc_in_date', 'adhoc_in_time']
        widgets = {
            'adhoc_in_date': forms.DateInput(attrs={'type': 'date'}),
            'adhoc_in_time': forms.TimeInput(attrs={'type': 'time'})
        }

    def clean(self):
        cleaned_data = super().clean()
        pgr = cleaned_data.get('pgr')
        adhoc_in_date = cleaned_data.get('adhoc_in_date')
        adhoc_in_time = cleaned_data.get('adhoc_in_time')
        adhoc_ticket = cleaned_data.get('adhoc_ticket')

        if pgr and adhoc_in_date and adhoc_in_time:
            try:
                requisition = AdhocManRequisition.objects.get(
                    pgr=pgr,
                    active_status=True,
                    start_date__lte=adhoc_in_date,
                    end_date__gte=adhoc_in_date,
                    level1_approval_status='Approved'
                )
            except AdhocManRequisition.DoesNotExist:
                raise forms.ValidationError("This adhoc has no active approval.")
            
            if not (requisition.start_date <= adhoc_in_date <= requisition.end_date):
                raise forms.ValidationError("In-date must be within the requisition's start and end dates.")

            # Check if the in-date and in-time already exist for the same PGR
            existing_attendance = AdhocAttendance.objects.filter(
                pgr=pgr,
                adhoc_in_date=adhoc_in_date,
                adhoc_in_time=adhoc_in_time
            ).exclude(id=self.instance.id)  
            if existing_attendance.exists():
                raise forms.ValidationError("In-date and in-time can only be assigned once within the same start and end dates.")

        # Validate if the ticket is already assigned to another PGR
        if adhoc_ticket:
            existing_ticket_attendance = AdhocAttendance.objects.filter(
                adhoc_ticket=adhoc_ticket
            ).exclude(pgr=pgr) 

            if existing_ticket_attendance.exists():
                raise forms.ValidationError(f"This ticket is already assigned to another PGR.")

        return cleaned_data






class AdhocAttendanceUpdateOuttimeForm(forms.ModelForm):
    class Meta:
        model = AdhocAttendance
        fields = ['pgr', 'adhoc_out_date', 'adhoc_out_time']
        widgets = {
            'adhoc_out_date': forms.DateInput(attrs={'type': 'date'}),
            'adhoc_out_time': forms.TimeInput(attrs={'type': 'time'})
        }

    def clean(self):
        cleaned_data = super().clean()
        adhoc_out_date = cleaned_data.get('adhoc_out_date')
        adhoc_out_time = cleaned_data.get('adhoc_out_time')

        if self.instance and adhoc_out_date and adhoc_out_time:
            pgr = self.instance.pgr  # Handle missing `pgr`
            if not pgr:
                raise ValidationError("PGR (Person Going Request) is required for this attendance record.")
            
            adhoc_in_date = self.instance.adhoc_in_date
            adhoc_in_time = self.instance.adhoc_in_time

            # Ensure `adhoc_in_date` and `adhoc_in_time` are present
            if not adhoc_in_date or not adhoc_in_time:
                raise ValidationError("In-time and in-date must be provided before setting out-time.")

            requisition = self.instance.get_active_requisition()

            if requisition:
                # Check if the out-date is within the requisition's start and end dates
                if not (requisition.start_date <= adhoc_out_date <= requisition.end_date):
                    raise ValidationError("Out-date must be within the requisition's start and end dates.")

                # Ensure out-time hasn't already been recorded for the same date and time
                existing_out_time = AdhocAttendance.objects.filter(
                    pgr=pgr,
                    adhoc_out_date=adhoc_out_date,
                    adhoc_out_time=adhoc_out_time
                ).exclude(id=self.instance.id)
                if existing_out_time.exists():
                    raise ValidationError("An entry with the same out-date and out-time already exists.")

                # Calculate working hours and bill amount
                in_datetime = datetime.combine(adhoc_in_date, adhoc_in_time)
                out_datetime = datetime.combine(adhoc_out_date, adhoc_out_time)

                # Ensure out-time is after in-time
                if out_datetime <= in_datetime:
                    raise ValidationError("Out-time must be after in-time.")

                self.instance.adhoc_working_hours = (out_datetime - in_datetime).total_seconds() / 3600  # in hours

               
                # Explicitly set the adhoc_requisition if it exists
                self.instance.adhoc_requisition = requisition
            else:
                raise ValidationError("No active requisition found for this attendance entry.")

        return cleaned_data


     

class AdhocPaymentForm(forms.ModelForm):
    class Meta:
        model = AdhocPayment
        exclude=['payment_id','created_at']




class PGRPaymentForm(forms.ModelForm):
    pgr_name = forms.CharField(max_length=255)

    class Meta:
        model = AdhocPayment
        exclude=['pgr','payment_id','created_at']

    def clean_pgr_name(self):
        pgr_name = self.cleaned_data['pgr_name']
        try:
            pgr = PGRdatabase.objects.get(name=pgr_name)
        except PGRdatabase.DoesNotExist:
            raise forms.ValidationError("PGR with this name does not exist.")
        return pgr




class PGRNameForm(forms.Form):
    pgr_name = forms.CharField(max_length=100, label='PGR Name')

