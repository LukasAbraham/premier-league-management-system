from django.shortcuts import render, redirect
from django.http import FileResponse
from django.contrib.auth import logout
from .models import Regulation
from apps.clubs.models import Club, ClubStats
from apps.players.models import PlayerStats
from apps.matches.models import Match, Result, GoalEvent
from .forms import RegulationForm
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa
from django.core.exceptions import ObjectDoesNotExist

def index(request):
    clubs = Club.objects.all()
    user = request.user
    context = {
        'clubs': clubs,
        'user': user,
    }
    return render(request, 'more/index.html',context)

def logout_user(request):
    logout(request)
    return redirect('/login')

def view_regulation(request):
    regulation = Regulation.objects.get(pk=1)
    user = request.user
    clubs = Club.objects.all()
    context = {
        'clubs': clubs,
        'user': user,
        'regulation': regulation,
    }
    return render(request, 'more/regulation.html',context)

def edit_regulation(request):
    regulation = Regulation.objects.get(pk=1)
    
    if request.method == "POST":
        form = RegulationForm(request.POST, instance=regulation)
        if form.is_valid():
            regulation = form.save()
            return redirect('/more')
    else:
        form = RegulationForm(instance=regulation)
    user = request.user
    clubs = Club.objects.all()
    context = {
        'form': form,
        'clubs': clubs,
        'user': user,
    }
    return render(request, 'more/edit_regulation.html',context)

def standing(request):
    club_stats = ClubStats.objects.all()
    standings = sorted(club_stats, key=lambda club_stat: (club_stat.points, club_stat.goal_difference), reverse=True)
    user = request.user
    clubs = Club.objects.all()
    context = {
        'standings': standings,
        'clubs': clubs,
        'user': user,
    }
    return render(request, 'more/standing.html',context)

def stats_records(request):
    player_stats = PlayerStats.objects.all()
    players_sorted_by_goals = sorted(player_stats, key=lambda player_stat: (player_stat.goals),reverse=True)
    players_sorted_by_assists = sorted(player_stats, key=lambda player_stat: (player_stat.assists),reverse=True)
    user = request.user
    clubs = Club.objects.all()
    context = {
        'top_scorers': players_sorted_by_goals,
        'top_play_makers': players_sorted_by_assists,
        'clubs': clubs,
        'user': user,
    }
    return render(request, 'more/stats_records.html',context)

def report(request):
    matches = Match.objects.all()
    goal_events = {}
    for match in matches:
        try:
            result = Result.objects.get(id=match.id)
            ge = GoalEvent.objects.filter(result=result)
        except ObjectDoesNotExist:
            result = None
            ge = None
        goal_events[match.id]=ge
    club_stats = ClubStats.objects.all()
    standings = sorted(club_stats, key=lambda club_stat: (club_stat.points, club_stat.goal_difference), reverse=True)
    player_stats = PlayerStats.objects.all()
    players_sorted_by_goals = sorted(player_stats, key=lambda player_stat: (player_stat.goals), reverse=True)
    players_sorted_by_assists = sorted(player_stats, key=lambda player_stat: (player_stat.assists), reverse=True)
    user = request.user
    clubs = Club.objects.all()
    context = {
        'top_scorers': players_sorted_by_goals,
        'top_play_makers': players_sorted_by_assists,
        'matches': matches,
        'clubs': clubs,
        'user': user,
        'standings': standings,
        'goal_events': goal_events,
    }
    return render(request, 'more/report.html', context)

def export_to_pdf(request):
    buffer = BytesIO()

    template = get_template('more/report.html')
    matches = Match.objects.all()
    goal_events = {}
    for match in matches:
        try:
            result = Result.objects.get(id=match.id)
            ge = GoalEvent.objects.filter(result=result)
        except ObjectDoesNotExist:
            result = None
            ge = None
        goal_events[match.id]=ge
    club_stats = ClubStats.objects.all()
    standings = sorted(club_stats, key=lambda club_stat: (club_stat.points, club_stat.goal_difference),reverse=True)
    player_stats = PlayerStats.objects.all()
    players_sorted_by_goals = sorted(player_stats, key=lambda player_stat: (player_stat.goals),reverse=True)
    players_sorted_by_assists = sorted(player_stats, key=lambda player_stat: (player_stat.assists),reverse=True)
    context = {
        'top_scorers': players_sorted_by_goals,
        'top_play_makers': players_sorted_by_assists,
        'matches': matches,
        'standings': standings,
        'goal_events': goal_events,
    }
    html = template.render(context)
    pisa.CreatePDF(BytesIO(html.encode('UTF-8')), buffer)
    buffer.seek(0)
    response = FileResponse(buffer, as_attachment=True, filename='pl_report.pdf')
    return response






