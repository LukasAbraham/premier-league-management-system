from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from .forms import PlayerForm, PlayerSearchForm
from .models import Player
from apps.clubs.models import Club
import re

def index(request):
    form = PlayerSearchForm(request.GET)
    players_list = Player.objects.select_related('club').all()
    if len(players_list) >= 5: 
        highlight_players = [players_list[i] for i in range(5)]
    else:
        highlight_players = []
    clubs = Club.objects.all()
    user = request.user
    context = {
        'user': user,
        'clubs': clubs,
        'highlight_players': highlight_players,
        'players_list': players_list,
        'form': form,
    }
    return render(request, 'players/index.html', context)

def add(request):
    submitted = False
    if request.method == "POST":
        form = PlayerForm(request.POST, request.FILES)
        if form.is_valid():
            player = form.save()
            if 'image' in request.FILES:
                if player.image:
                    player.image.delete(save=False)
                player.image = request.FILES['image']
                player.image.name = f'player_{player.club.id}_{player.id}.png'
                player.save()

            return HttpResponseRedirect('/players/add?submitted=True')
    else:
        form = PlayerForm()
        if 'submitted' in request.GET:
            submitted = True
    user = request.user
    clubs = Club.objects.all()
    context = {
        'user': user,
        'form': form,
        'submitted': submitted,
        'clubs': clubs,
    }
    return render(request, 'players/add.html', context)

def view(request, player_id):
    player = Player.objects.get(pk=player_id)
    user = request.user
    clubs = Club.objects.all()
    context = {
        'user': user,
        'clubs': clubs,
        'player': player,
    }
    return render(request, 'players/view.html', context)  

def edit(request, player_id):
    player = Player.objects.get(pk=player_id)
    
    if request.method == "POST":
        form = PlayerForm(request.POST, request.FILES, instance=player)
        if form.is_valid():
            player = form.save()
            if 'image' in request.FILES:
                if player.image:
                    player.image.delete(save=False)
                player.image = request.FILES['image']
                player.image.name = f'player_{player.club.id}_{player.id}.png'
                player.save()
            return redirect('/players')
    else:
        form = PlayerForm(instance=player)
    user = request.user
    clubs = Club.objects.all()
    context = {
        'user': user,
        'form': form,
        'clubs': clubs,
    }
    return render(request, 'players/add.html', context)

def delete(request, player_id):
    player = Player.objects.get(pk=player_id)
    player.delete()
    return redirect('/players')

def search(request):
    form = PlayerSearchForm(request.GET)
    found_players = None
    if form.is_valid():
        player_name = form.cleaned_data['name']
        found_players = Player.objects.filter(name__iregex=r'^.*{}.*$'.format(re.escape(player_name)))
    user = request.user
    clubs = Club.objects.all()
    context = {
        'form': form,
        'clubs': clubs,
        'found_players': found_players,
        'user': user,
    }
    return render(request, 'players/search.html', context)