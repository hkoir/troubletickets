from django import forms
from.models import AddPGInfo,PGFaultRecord,PGFuelRefill
from common.models import Region,Zone,MP


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
 


from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES

class PGDatabaseViewForm(forms.Form):   
    region = forms.ChoiceField(choices=REGION_CHOICES, required=False)
    zone = forms.ChoiceField(choices=ZONE_CHOICES, required=False)
    mp = forms.ChoiceField(choices=MP_CHOICES, required=False)
    PGNumber = forms.CharField(required=False)
   
    # class Meta:
    #     model = AddPGInfo
    #     fields = ['PGNumber'] 





class PGFuelRefillForm(forms.ModelForm):
    refill_date = forms.DateField(label='PG refil date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    pgnumber = forms.ModelChoiceField(queryset=AddPGInfo.objects.all(), required=False, label='PG Number', widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = PGFuelRefill
        exclude = ['fuel_refill_code', 'refill_requester', 'fuel_cost', 'created_at'] 

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







