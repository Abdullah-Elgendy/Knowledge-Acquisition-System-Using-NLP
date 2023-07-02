from django.forms import ModelForm 
from django import forms
from . models import Project


class projectDataForm(ModelForm):
    class Meta:
        model = Project
        fields = ["Title" , "Description" , "Url_1" , "Url_2" , "Url_3" , "Url_4"]

class fileUploadForm(forms.Form):
    file = forms.FileField()
    
        