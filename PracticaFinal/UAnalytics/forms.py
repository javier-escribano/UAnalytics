from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout
from crispy_forms.layout import Field
from crispy_forms.layout import Fieldset
from crispy_forms.layout import HTML
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class NewTwitchForm(forms.Form):
    usuario= forms.CharField(label='', max_length=32, required=True, widget=forms.TextInput(attrs={'placeholder': 'Username', 'size':40}))

    def __init__(self, *args, **kwargs):
        super(NewTwitchForm,self).__init__(*args,**kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-newProductForm'
        self.helper.form_method = 'post'
        self.helper.form_action = 'twitch'
        self.helper.add_input(Submit('submit','Buscar'))
    
    
class NewYTForm(forms.Form):
    usuario= forms.CharField(label='', max_length=32, required=True, widget=forms.TextInput(attrs={'placeholder': 'Username', 'size':40}))

    def __init__(self, *args, **kwargs):
        super(NewYTForm,self).__init__(*args,**kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-newProductForm'
        self.helper.form_method = 'post'
        self.helper.form_action = 'youtube'
        self.helper.add_input(Submit('submit','Buscar'))


class NewTwitterForm(forms.Form):
    usuario= forms.CharField(label='', max_length=32, required=True, widget=forms.TextInput(attrs={'placeholder': 'Username', 'size':40}))

    def __init__(self, *args, **kwargs):
        super(NewTwitterForm,self).__init__(*args,**kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-newProductForm'
        self.helper.form_method = 'post'
        self.helper.form_action = 'twitter'
        self.helper.add_input(Submit('submit','Buscar'))