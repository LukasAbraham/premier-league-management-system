from django import forms
from django.forms import ModelForm
from .models import Manager
from apps.more.models import Regulation
from django.forms import widgets
from datetime import date

class ManagerSearchForm(forms.Form):
    manager_name = forms.CharField(label='Manager name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search', 'name': 'manager_name'}))

class ManagerForm(ModelForm):
    class Meta:
        model = Manager
        fields = "__all__"
    
    dob = forms.DateField(widget=widgets.DateInput(attrs={'type': 'date'}), initial=date.today())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def label_tag(self, label=None, attrs=None, label_suffix=None):
        attrs = attrs or {}
        attrs['class'] = 'form-label'
        return super().label_tag(label, attrs, label_suffix)

    def clean(self):
        cleaned_data = super().clean()
        dob = cleaned_data.get('dob')
        regulation = Regulation.objects.get(pk=1)
        if dob:
            today = date.today()
            age = today.year - dob.year

            if age < regulation.manager_min_age or age > regulation.manager_max_age:
                self.add_error('dob', "Invalid date of birth. Manager's age must be between " + str(regulation.manager_min_age) + " and " + str(regulation.manager_max_age) + " years of age.")
    