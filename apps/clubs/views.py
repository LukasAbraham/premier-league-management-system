from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from .forms import ClubForm, ClubSearchForm
from .models import Club 
from apps.managers.models import Manager
from apps.more.models import Regulation
import re

def update_clubs_status():
    regulation = Regulation.objects.get(pk=1)
    clubs = Club.objects.all()
    for club in clubs:
        club.update_status(max_foreign_players=regulation.max_foreign_players, max_players=regulation.max_players, min_players=regulation.min_players)
        
def index(request):
    form = ClubSearchForm(request.GET)
    update_clubs_status()
    clubs = Club.objects.all()
    user = request.user
    context = {
        'clubs': clubs,
        'user': user,
        'form': form,
    }
    return render(request, 'clubs/index.html',context)

def logout_user(request):
    logout(request)
    return redirect('/auth/')

def add(request):
    submitted = False
    if request.method == "POST":
        form = ClubForm(request.POST, request.FILES)
        if form.is_valid():
            club = form.save()
            if 'logo' in request.FILES:
                if club.logo:
                    club.logo.delete(save=False)
                club.logo = request.FILES['logo']
                club.logo.name = f'club_{club.id}.png'
                club.save()
            return HttpResponseRedirect('/club/add?submitted=True')
    else:
        form = ClubForm()
        if 'submitted' in request.GET:
            submitted = True
    user = request.user
    clubs = Club.objects.all()
    context = {
        'form': form,
        'submitted': submitted,
        'clubs': clubs,
        'user': user,
    }
    return render(request, 'clubs/add.html',context)

def view(request, club_id):
    club = Club.objects.get(pk=club_id)
    has_manager = Manager.objects.filter(club=club).exists()
    user = request.user
    clubs = Club.objects.all()
    context = {
        'clubs': clubs,
        'club': club,
        'has_manager': has_manager,
        'user': user,
    }
    return render(request, 'clubs/view.html',context)

def edit(request, club_id):
    club = Club.objects.get(pk=club_id)
    
    if request.method == "POST":
        form = ClubForm(request.POST, request.FILES, instance=club)
        if form.is_valid():
            club = form.save()
            if 'logo' in request.FILES:
                if club.logo:
                    club.logo.delete(save=False)
                club.logo = request.FILES['logo']
                club.logo.name = f'club_{club.id}.png'
                club.save()
            return redirect('/clubs')
    else:
        form = ClubForm(instance=club)
    user = request.user
    clubs = Club.objects.all()
    context = {
        'form': form,
        'clubs': clubs,
        'user': user,
    }
    return render(request, 'clubs/add.html',context)

def delete(request, club_id):
    club = Club.objects.get(pk=club_id)
    club.delete()
    return redirect('/clubs')

def search(request):
    form = ClubSearchForm(request.GET)
    found_clubs = None
    if form.is_valid():
        club_name = form.cleaned_data['name']
        found_clubs = Club.objects.filter(name__iregex=r'^.*{}.*$'.format(re.escape(club_name)))
    user = request.user
    clubs = Club.objects.all()
    context = {
        'form': form,
        'clubs': clubs,
        'found_clubs': found_clubs,
        'user': user,
    }
    return render(request, 'clubs/search.html', context)