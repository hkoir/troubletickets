from django import forms
from.models import Region,Zone,MP
from.models import FuelPumpDatabase,PGRdatabase




class CombinedForm(forms.Form):
    region_name = forms.CharField(max_length=100, required=False, label='New Region')
    zone_name = forms.CharField(max_length=100, required=False, label='New Zone')
    mp_name = forms.CharField(max_length=100, label='MP')
    
    region_id = forms.ModelChoiceField(queryset=Region.objects.all(), required=False, label='Select Existing Region')
    zone_id = forms.ModelChoiceField(queryset=Zone.objects.all(), required=False, label='Select Existing Zone')

    def clean(self):
        cleaned_data = super().clean()
        region_name = cleaned_data.get('region_name')
        region_id = cleaned_data.get('region_id')
        zone_name = cleaned_data.get('zone_name')
        zone_id = cleaned_data.get('zone_id')

        if not region_name and not region_id:
            raise forms.ValidationError('You must specify a new region or select an existing one.')

        if not zone_name and not zone_id:
            raise forms.ValidationError('You must specify a new zone or select an existing one.')

        return cleaned_data

    def save(self):
        cleaned_data = self.cleaned_data
        region = cleaned_data.get('region_id')
        if not region:
            region, created = Region.objects.get_or_create(name=cleaned_data['region_name'])

        zone = cleaned_data.get('zone_id')
        if not zone:
            zone, created = Zone.objects.get_or_create(name=cleaned_data['zone_name'], region=region)

        mp, created = MP.objects.get_or_create(name=cleaned_data['mp_name'], zone=zone)

        return region, zone, mp



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
    



class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()
