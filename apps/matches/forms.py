from django import forms
from django.core.exceptions import ValidationError
from .models import Match, Result, GoalEvent
from apps.clubs.models import Club 
from apps.players.models import Player
from apps.more.models import Regulation
from django.forms import widgets, BaseFormSet
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import date

class MatchForm(forms.ModelForm):
    class Meta: 
        model = Match
        fields = ['round', 'time', 'club1', 'club2']
        
    time = forms.DateTimeField(widget=widgets.DateTimeInput(attrs={'type': 'datetime-local'}), initial=timezone.now())
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        valid_clubs = Club.objects.filter(status='V')
        self.fields['club1'].queryset = valid_clubs
        self.fields['club2'].queryset = valid_clubs
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super().clean()
        club1 = cleaned_data.get('club1')
        club2 = cleaned_data.get('club2')
        round = cleaned_data.get('round')
        
        if club1 == club2:
            raise ValidationError("A club cannot compete against itself.")
        
        if club1.status == 'I':
            raise ValidationError(f"{club1.name} is not valid to compete.")
        
        if club2.status == 'I':
            raise ValidationError(f"{club2.name} is not valid to compete.")
        
        if Match.objects.filter(round=round, club1=club1).exists() or Match.objects.filter(round=round, club2=club1).exists():
            raise ValidationError(f"{club1.name} has already competed in round {round}.")
        
        if Match.objects.filter(round=round, club1=club2).exists() or Match.objects.filter(round=round, club2=club2).exists():
            raise ValidationError(f"{club2.name} has already competed in round {round}.")

        
class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        exclude = ['match']
    
    def __init__(self, *args, **kwargs):
        self.match = kwargs.pop('match', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def clean(self):
        super().clean()
        if self.match and self.match.status != 'P':
            raise ValidationError("Cannot add a result to a match that hasn't happened yet.")

        
class GoalEventForm(forms.ModelForm):
    class Meta:
        model = GoalEvent
        fields = ['scoring_player', 'assisting_player', 'type', 'time', 'club']
    
    def __init__(self, *args, **kwargs):
        self.match = kwargs.pop('match', None)
        super().__init__(*args, **kwargs)
        if self.match: 
            self.fields['club'].queryset = Club.objects.filter(id__in=[self.match.club1.id, self.match.club2.id])
            self.fields['scoring_player'].queryset = Player.objects.filter(
                club__in=[self.match.club1, self.match.club2]
            )
            self.fields['assisting_player'].queryset = Player.objects.filter(
                club__in=[self.match.club1, self.match.club2]
            )
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
    def clean(self):
        cleaned_data = super().clean()
        club = cleaned_data.get('club')
        scoring_player = cleaned_data.get('scoring_player')
        assisting_player = cleaned_data.get('assisting_player')
        time = cleaned_data.get('time')
        type = cleaned_data.get('type')
        
        regulation = Regulation.objects.get(pk=1)
        
        if (scoring_player and assisting_player) and scoring_player == assisting_player:
            self.add_error("assisting_player", "A player cannot assist himself")
        if (scoring_player and assisting_player) and scoring_player.club != assisting_player.club:
            self.add_error("scoring_player", "Scoring player and assisting player must be in the same club!")
            self.add_error("assisting_player", "Scoring player and assisting player must be in the same club!")
        if (club and scoring_player and type) and (scoring_player.club != club and type != 'OG'):
            self.add_error("type", "If a player scored for the opposing club then the goal type must be 'Own goal'")
        if time and time > regulation.duration:
            self.add_error('time', f"Invalid goal scoring time. The match duration is only {regulation.duration} minutes")
        if club and club not in [self.match.club1, self.match.club2]:
            self.add_error('club', "The club must be one of the clubs playing in the match.")
        if self.match.status != 'P':
            raise ValidationError("Cannot add a goal event to a match that hasn't happened yet.")
        return cleaned_data
    
class BaseGoalEventFormSet(BaseFormSet):
    def clean(self):
        super().clean()

        club1_goals = 0
        club2_goals = 0

        for form in self.forms:
            if not form.is_valid():
                raise ValidationError("Submission failed because there are still invalid forms")
            if form.cleaned_data['club'] == self.forms[0].match.club1:
                club1_goals += 1
            elif form.cleaned_data['club'] == self.forms[0].match.club2:
                club2_goals += 1

        result = get_object_or_404(Result, match=self.forms[0].match)
        if club1_goals != result.club1_goals or club2_goals != result.club2_goals:
            raise ValidationError("The number of goals event for each club must match the goals in the result")

        