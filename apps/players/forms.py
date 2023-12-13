from django import forms
from django.forms import ModelForm
from .models import Player, PlayerStats
from apps.more.models import Regulation
from django.forms import widgets
from datetime import date

class PlayerSearchForm(forms.Form):
    player_name = forms.CharField(label='Player Name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search', 'name': 'player_name'}))

class PlayerForm(ModelForm):
    class Meta:
        model = Player
        exclude = ['type']
    
    dob = forms.DateField(widget=widgets.DateInput(attrs={'type': 'date'}), initial=date.today())
    # image = forms.ImageField(required=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['height'].label += ' (cm)'
        self.fields['weight'].label += ' (kg)'
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def label_tag(self, label=None, attrs=None, label_suffix=None):
        attrs = attrs or {}
        attrs['class'] = 'form-label'
        return super().label_tag(label, attrs, label_suffix)
    
    def save(self, commit=True):
        player = super().save(commit=commit)
        if commit:
            if player.nationality == 'English':
                player.type = 'HG'
            else:
                player.type = 'FR'
            player.save()
        else:
            player = None
        return player

    def clean(self):
        cleaned_data = super().clean()
        dob = cleaned_data.get('dob')
        regulation = Regulation.objects.get(pk=1)
        # Check if the player's birthdate is valid
        if dob:
            today = date.today()
            age = today.year - dob.year

            if age < regulation.player_min_age or age > regulation.player_max_age:
                self.add_error('dob', "Invalid date of birth. Player's age must be between " + str(regulation.player_min_age) + " and " + str(regulation.player_max_age) + " years of age")
        return cleaned_data
    