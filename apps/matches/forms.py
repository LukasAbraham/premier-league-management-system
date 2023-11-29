from django import forms
from django.core.exceptions import ValidationError
from .models import Match, Result, GoalEvent
from apps.clubs.models import Club 
from apps.players.models import Player
from apps.more.models import Regulation
from django.forms import widgets
from django.utils import timezone
from datetime import date
from django.forms import formset_factory

class MatchForm(forms.ModelForm):
    class Meta: 
        model = Match
        fields = ['round', 'time', 'club1', 'club2']
        
    time = forms.DateTimeField(widget=widgets.DateTimeInput(attrs={'type': 'datetime-local'}), initial=timezone.now())
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super().clean()
        club1 = cleaned_data.get('club1')
        club2 = cleaned_data.get('club2')
        round = cleaned_data.get('round')
        
        if club1 == club2:
            raise ValidationError("A club cannot compete against itself.")
        
        if Match.objects.filter(round=round, club1=club1).exists() or Match.objects.filter(round=round, club2=club1).exists():
            raise ValidationError(f"{club1.name} has already competed in round {round}.")
        
        if Match.objects.filter(round=round, club1=club2).exists() or Match.objects.filter(round=round, club2=club2).exists():
            raise ValidationError(f"{club2.name} has already competed in round {round}.")

        
class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        exclude = ['match']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    # def clean(self):
        # cleaned_data = super().clean()
        # match = cleaned_data.get('match')
        # match = self.instance.match
        
        # if match.status != 'P':
            # raise ValidationError("Cannot add a result to a match that hasn't happened yet.")
        
class GoalEventForm(forms.ModelForm):
    class Meta:
        model = GoalEvent
        fields = ['scoring_player', 'assisting_player', 'type', 'time', 'club']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.match: 
            self.fields['club'].queryset = Club.objects.filter(id__in=[self.instance.match.club1.id, self.instance.match.club2.id])
            self.fields['scoring_player'].queryset = Player.objects.filter(
                club__in=[self.instance.match.club1, self.instance.match.club2]
            )
            self.fields['assisting_player'].queryset = Player.objects.filter(
                club__in=[self.instance.match.club1, self.instance.match.club2]
            )
            
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
    # def clean(self):
    #     cleaned_data = super().clean()
    #     match = cleaned_data.get('match')
    #     club = cleaned_data.get('club')
    #     if match.status != 'P':
    #         raise ValidationError("Cannot add a goal event to a match that hasn't happened yet.")
    #     if club not in [match.club1, match.club2]:
    #         raise ValidationError("The club must be one of the clubs playing in the match.")
    #     return cleaned_data
    