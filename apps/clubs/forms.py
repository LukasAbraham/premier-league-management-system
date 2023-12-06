from django import forms
from django.forms import ModelForm, formset_factory
from .models import Club, Achievement
from datetime import date

class ClubSearchForm(forms.Form):
    club_name = forms.CharField(label='Club name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search', 'name': 'club_name'}))

class ClubForm(ModelForm):
    class Meta:
        model = Club
        exclude = ['status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    # Add Bootstrap classes to form labels
    def label_tag(self, label=None, attrs=None, label_suffix=None):
        attrs = attrs or {}
        attrs['class'] = 'form-label'
        return super().label_tag(label, attrs, label_suffix)
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('established_year') > date.today().year:
            self.add_error('established_year', "Invalid club's established year!")
        return cleaned_data
    
class AchievementForm(ModelForm):
    class Meta:
        model = Achievement
        fields = ['cup', 'year']
     
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('year') > date.today().year:
            self.add_error('year', "Invalid year")
        return cleaned_data
            
AchievementFormSet = formset_factory(AchievementForm, extra=1)

    