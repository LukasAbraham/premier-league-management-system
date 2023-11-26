from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from .forms import ManagerForm, ManagerSearchForm
from .models import Manager
from apps.clubs.models import Club
import re

def index(request):
    form = ManagerSearchForm(request.GET)
    managers_list = Manager.objects.all()
    clubs = Club.objects.all()
    user = request.user
    context = {
        'clubs': clubs,
        'managers_list': managers_list,
        'user': user,
        'form':form,
    }
    return render(request, 'managers/index.html', context)

def logout_user(request):
    logout(request)
    return redirect('/auth')

def add(request):
    submitted = False
    if request.method == "POST":
        form = ManagerForm(request.POST, request.FILES)
        if form.is_valid():
            manager = form.save()
            if 'image' in request.FILES:
                if manager.image:
                    manager.image.delete(save=False)
                manager.image = request.FILES['image']
                manager.image.name = f'manager_{manager.club.id}_{manager.id}.png'
                manager.save()
            return HttpResponseRedirect('/managers/add?submitted=True')
    else:
        form = ManagerForm()
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
    return render(request, 'managers/add.html',context)

def view(request, manager_id):
    manager = Manager.objects.get(pk=manager_id)
    user = request.user
    clubs = Club.objects.all()
    context = {
        'user': user,
        'clubs': clubs,
        'manager': manager
    }
    return render(request, 'managers/view.html',context)

def edit(request, manager_id):
    manager = Manager.objects.get(pk=manager_id)
    
    if request.method == "POST":
        form = ManagerForm(request.POST, request.FILES, instance=coach)
        if form.is_valid():
            manager = form.save()
            if 'image' in request.FILES:
                if manager.image:
                    manager.image.delete(save=False)
                manager.image = request.FILES['image']
                manager.image.name = f'manager_{manager.club.id}_{manager.id}.png'
                manager.save()
            return redirect('/managers')
    else:
        form = ManagerForm(instance=manager)
    user = request.user
    clubs = Club.objects.all()
    context = {
        'form': form,
        'clubs': clubs,
        'user': user,
    }
    return render(request, 'managers/add.html',context)

def delete(request, manager_id):
    manager = Manager.objects.get(pk=manager_id)
    manager.delete()
    return redirect('/managers')

def search(request):
    form = ManagerSearchForm(request.GET)
    found_managers = None
    if form.is_valid():
        manager_name = form.cleaned_data['name']
        found_managers = Manager.objects.filter(name__iregex=r'^.*{}.*$'.format(re.escape(manager_name)))
    user = request.user
    clubs = Club.objects.all()
    context = {
        'form': form,
        'clubs': clubs,
        'found_managers': found_managers,
        'user': user,
    }
    return render(request, 'managers/search.html', context)