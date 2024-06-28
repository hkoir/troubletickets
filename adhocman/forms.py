from django import forms
from common.models import PGRdatabase
from .models import AdhocRequisition,AdhocAttendance,AdhocPayment
from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES





class AdhocRequisitionForm(forms.ModelForm):

    class Meta: 
        model = AdhocRequisition
        fields = ['pgr','start_date','end_date','purpose']

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


from django.core.exceptions import ValidationError

class AdhocAttendanceIntimeForm(forms.ModelForm):
    class Meta:
        model = AdhocAttendance
        fields=['pgr','adhoc_in_date','adhoc_in_time','adhoc_pay_rate']
        widgets = {
                'adhoc_in_date': forms.TimeInput(attrs={'type': 'date'}),
                'adhoc_in_time': forms.TimeInput(attrs={'type': 'time'})
        }

    def clean(self):
        cleaned_data = super().clean()
        pgr = cleaned_data.get('pgr')
        adhoc_in_date = cleaned_data.get('adhoc_in_date')
        adhoc_in_time = cleaned_data.get('adhoc_in_time')

        if pgr and adhoc_in_date and adhoc_in_time:
            try:
                requisition = AdhocRequisition.objects.get(
                    pgr=pgr,
                    active_status=True,
                    start_date__lte=adhoc_in_date,
                    end_date__gte=adhoc_in_date,
                    level1_approval_status='Approved'
                )
            except AdhocRequisition.DoesNotExist:
                raise ValidationError("This adhoc has no active approval.")

            if not (requisition.start_date <= adhoc_in_date <= requisition.end_date):
                raise ValidationError("In-date must be within the requisition's start and end dates.")

            existing_attendance = AdhocAttendance.objects.filter(
                pgr=pgr,
                adhoc_in_date=adhoc_in_date,
                adhoc_in_time=adhoc_in_time
            ).exclude(id=self.instance.id)
            if existing_attendance.exists():
                raise ValidationError("In-date and in-time can be given only once within the same start-date and end-date.")

        return cleaned_data

            
                     
from datetime import datetime

class AdhocAttendanceUpdateOuttimeForm(forms.ModelForm):
    class Meta:
        model = AdhocAttendance
        fields=['pgr','adhoc_out_date','adhoc_out_time']

        widgets = {
                'adhoc_out_date': forms.TimeInput(attrs={'type': 'date'}),
                'adhoc_out_time': forms.TimeInput(attrs={'type': 'time'})
        }

        def clean(self):
            cleaned_data = super().clean()
            pgr = self.instance.pgr
            adhoc_in_date = self.instance.adhoc_in_date
            adhoc_in_time = self.instance.adhoc_in_time
            adhoc_out_date = cleaned_data.get('adhoc_out_date')
            adhoc_out_time = cleaned_data.get('adhoc_out_time')

            if adhoc_out_date and adhoc_out_time:
                requisition = self.instance.get_active_requisition()
                if requisition:
                    if not (requisition.start_date <= adhoc_out_date <= requisition.end_date):
                        raise ValidationError("Out-date must be within the requisition's start and end dates.")

                    existing_out_time = AdhocAttendance.objects.filter(
                        pgr=pgr,
                        adhoc_out_date=adhoc_out_date,
                        adhoc_out_time=adhoc_out_time
                    ).exclude(id=self.instance.id)
                    if existing_out_time.exists():
                        raise ValidationError("Out-time can be given only once within the same start-date and end-date.")

                    in_datetime = datetime.combine(adhoc_in_date, adhoc_in_time)
                    out_datetime = datetime.combine(adhoc_out_date, adhoc_out_time)
                    self.instance.adhoc_working_hours = out_datetime - in_datetime
                    self.instance.adhoc_bill_amount = (self.instance.adhoc_working_hours.total_seconds() / 3600) * float(self.instance.adhoc_pay_rate)

            return cleaned_data

            
                     



class AdhocPaymentForm(forms.ModelForm):
    class Meta:
        model = AdhocPayment
        exclude=['payment_id','created_at']

      