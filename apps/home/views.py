from django.shortcuts import render, redirect
from django.contrib.auth import logout
from apps.clubs.models import Club, ClubStats
from apps.players.models import Player, PlayerStats
from apps.managers.models import Manager

def index(request):
    clubs = Club.objects.all()
    club_stats = ClubStats.objects.all()
    top_clubs = sorted(club_stats, key=lambda club: (club.points, club.goal_difference), reverse=True)[:4]
    player_stats = PlayerStats.objects.all()
    top_players = sorted(player_stats, key=lambda player: (player.goals), reverse=True)[:3]
    user = request.user
    context = {
        'clubs': clubs,
        'top_clubs': top_clubs,
        'top_players': top_players,
        'user': user,
    }
    return render(request, 'home/index.html', context)

