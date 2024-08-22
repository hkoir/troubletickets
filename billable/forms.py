from django import forms
from .models import CivilPower,ChatMessage

from tickets.mp_list import REGION_CHOICES,ZONE_CHOICES,MP_CHOICES







class ChatForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'placeholder': 'Enter your message here...'})
        }


class CivilPowerRequisition(forms.ModelForm):
    TT_open_date = forms.DateField(label='TT open_date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
   
    class Meta:
        model = CivilPower
        fields = ['region','zone','task_name','task_description','SOR_rate','qty','site_code','TT_number','requisition_amount','supporting_documents','TT_open_date']




class ApprovalForm(forms.ModelForm):
    class Meta:
        model = CivilPower
        fields = [] 

    def __init__(self, *args, **kwargs):
        user_level = kwargs.pop('user_level', None)
        super(ApprovalForm, self).__init__(*args, **kwargs)
        if user_level == 'level1':
            self.fields['level1_approval_status'] = forms.ChoiceField(choices=CivilPower.APPROVAL_STATUS_CHOICES)
            self.fields['level1_comments'] = forms.TextField()
        elif user_level == 'level2':
            self.fields['level2_approval_status'] = forms.ChoiceField(choices=CivilPower.APPROVAL_STATUS_CHOICES)
            self.fields['level2_comments'] = forms.TextField()
        elif user_level == 'level3':
            self.fields['level3_approval_status'] = forms.ChoiceField(choices=CivilPower.APPROVAL_STATUS_CHOICES)
            self.fields['level3_comments'] = forms.TextField()



class ExpenseRequisitionStatusForm(forms.Form):
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





class MoneySendingForm(forms.ModelForm):   
    TakePicture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'accept': 'image/*', 'capture': 'camera'}))  # File input field with 'capture' attribute for camera capture
    UploadPicture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}))  # File input field without 'capture' attribute for file selection  
  
    class Meta:
        model =  CivilPower
        fields = ['money_sending_date']      
        widgets = {
                'money_sending_date': forms.TimeInput(attrs={'type': 'date'})          
            
                     }
        
    def clean(self):
        cleaned_data = super().clean()
        upload_picture = cleaned_data.get('UploadPicture')
        take_picture = cleaned_data.get('TakePicture')

        if upload_picture and take_picture:
            raise forms.ValidationError("Please choose either Upload Picture or Take Picture, not both.")

        return cleaned_data
    


class WorkUpdateForm(forms.ModelForm):   
    TakePicture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'accept': 'image/*', 'capture': 'camera'}))  # File input field with 'capture' attribute for camera capture
    UploadPicture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}))  # File input field without 'capture' attribute for file selection  
  
    class Meta:
        model =  CivilPower
        fields = ['actual_cost','work_completion_date','TT_status','TT_close_date']      
     
        widgets = {'work_completion_date': forms.TimeInput(attrs={'type': 'date'}),
                   'TT_close_date': forms.TimeInput(attrs={'type': 'date'})}
        
        
    def clean(self):
        cleaned_data = super().clean()
        upload_picture = cleaned_data.get('UploadPicture')
        take_picture = cleaned_data.get('TakePicture')

        if upload_picture and take_picture:
            raise forms.ValidationError("Please choose either Upload Picture or Take Picture, not both.")

        return cleaned_data