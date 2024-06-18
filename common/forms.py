from django import forms
from.models import FuelPumpDatabase,PGRdatabase

from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES




class FuelPumpDatabaseForm(forms.ModelForm):
    contact_date = forms.DateField(label='contact date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = FuelPumpDatabase
        exclude =['created_at','fuel_pump_id']        



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
    



class PGRViewForm(forms.Form):
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

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()
