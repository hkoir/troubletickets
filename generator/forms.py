from django import forms
from.models import AddPGInfo,PGFaultRecord,PGFuelRefill
from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES

from.models import Region,Zone,MP


class AddPgForm(forms.ModelForm):
    PG_purchase_date = forms.DateField(label='PG_purchase_date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    PG_hire_date  = forms.DateField(label='PG_hire_date ', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = AddPGInfo
        exclude = ['PG_add_requester','created_at','PG_code','updated_at'] 
 


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
    region = forms.ChoiceField(
        label ='Select Region',
        required = False,
      

    )

    zone = forms.ChoiceField(
        label ='Select zone',
        required = False,
     

    )

    mp = forms.ChoiceField(
        label ='Select MP',
        required = False,
 

    )

    PGNumber = forms.CharField(label='PGNumber', required=False)  

    class Meta:
        model = AddPGInfo
        fields = ['region',' zone','mp','PGNumber'] 




class PGFuelRefillForm(forms.ModelForm):   
    refill_date = forms.DateField(label='PG refil date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = PGFuelRefill
        exclude = ['fuel_refill_code','refill_date','refill_requester','fuel_cost','created_at'
                   
                   ] 
        widgets = {
            'pgnumber': forms.Select(attrs={'class': 'form-control'}),
        }


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
    pg_number = forms.CharField(label='PG Number', max_length=50)










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

