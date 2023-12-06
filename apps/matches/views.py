from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Match, Result, GoalEvent
from apps.players.models import Player
from apps.clubs.models import Club 
from .forms import MatchForm, ResultForm, GoalEventForm, BaseGoalEventFormSet
from django.utils import timezone
from django.forms import formset_factory
from django.core.exceptions import ObjectDoesNotExist

def index(request):
    clubs = Club.objects.all()
    matches = Match.objects.all()
    for match in matches:
        if match.time < timezone.now():
            match.status = "P"
        else:
            match.status = "U"
        match.save()
    matches_list = matches.order_by('-time')
    user = request.user
    context = {
        'clubs': clubs,
        'matches_list': matches_list,
        'user': user,
    }
    return render(request, 'matches/index.html', context)

def add(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/matches")
    else:
        form = MatchForm()
    
    user = request.user
    clubs = Club.objects.all()
    context = {
        'form': form,
        'clubs': clubs,
        'user': user,
    }
    return render(request, 'matches/add.html', context)

def add_result(request, match_id):
    match = Match.objects.get(id=match_id)
    if request.method == 'POST':
        form = ResultForm(request.POST, match=match)
        if form.is_valid():
            result = form.save(commit=False)
            result.match = match
            result.save()
            return redirect(reverse('matches:add_goal_events', args=[match.id]))
    else:
        form = ResultForm(match=match)
        
    user = request.user
    clubs = Club.objects.all()
    context = {
        'form': form,
        'clubs': clubs,
        'user': user,
        'match': match,
    }
    return render(request, 'matches/add_result.html', context)

def add_goal_events(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    result = get_object_or_404(Result, match=match)
    total_goals = result.club1_goals + result.club2_goals
    GoalEventFormSet = formset_factory(GoalEventForm, extra=total_goals, formset=BaseGoalEventFormSet)
    if request.method == 'POST':
        formset = GoalEventFormSet(request.POST, form_kwargs={'match': match})
        if formset.is_valid():
            for form in formset:
                goal_event = form.save(commit=False)
                goal_event.match = match
                goal_event.save()
            return redirect(reverse('matches:index'))
    else:
        formset = GoalEventFormSet(form_kwargs={'match': match})
        # Filter players from the clubs participating in the match
        club1_players = Player.objects.filter(club=match.club1)
        club2_players = Player.objects.filter(club=match.club2)
        valid_players = club1_players | club2_players
        for form in formset:
            form.fields['scoring_player'].queryset = valid_players
            form.fields['assisting_player'].queryset = valid_players
            
    user = request.user
    clubs = Club.objects.all()
    context = {
        'user': user,
        'clubs': clubs,
        'match': match,
        'formset': formset,
    }
    return render(request, 'matches/add_goal_events.html', context)


def edit(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    old_match = Match.objects.get(pk=match_id)
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            match.update(old_match)
            return redirect('/matches')
    else:
        form = MatchForm(instance=match)
        
    user = request.user
    clubs = Club.objects.all()
    context = {
        'user': user,
        'clubs': clubs,
        'match': match,
        'form': form,
    }
    return render(request, 'matches/add.html', context)

def delete(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    match.delete()
    return redirect('/matches')

def view(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    try:
        result = Result.objects.get(match=match)
        goal_events = GoalEvent.objects.filter(match=match)
    except ObjectDoesNotExist:
        result = None
        goal_events = None
    user = request.user
    clubs = Club.objects.all()
    context = {
        'result': result,
        'match': match,
        'clubs': clubs,
        'goal_events': goal_events,
        'user': user,
    }

    return render(request, 'matches/view.html', context)
