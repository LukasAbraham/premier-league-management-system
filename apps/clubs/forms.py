from django import forms
from django.forms import ModelForm
from .models import Club

class ClubSearchForm(forms.Form):
    club_name = forms.CharField(label='Club name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search', 'name': 'club_name'}))

class ClubForm(ModelForm):
    class Meta:
        model = Club
        exclude = ['status']
    
    sponsor_choice = forms.ChoiceField(choices=Club.SPONSOR_CHOICES)
    
    stadium_choice = forms.ChoiceField(choices=Club.STADIUM_CHOICES)
    
    club_logo = forms.ImageField(required=True)
    
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