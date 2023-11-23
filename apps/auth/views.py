from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import UserProfile

def sign_up(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            key = form.cleaned_data['key']
            user = form.save()
            if key == 'admin':
                UserProfile.objects.create(user=user, user_type='admin')
            else:
                UserProfile.objects.create(user=user, user_type='user')
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("You have signed up successful!"))
            return redirect('/')
    else:
        form = SignUpForm()
    return render(request, 'auth/sign_up.html', {'form': form},)

def sign_in(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        remember_me = request.POST.get('remember_me')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if remember_me == 'on':
                request.session.set_expiry(2592000)
                request.session['remember_me'] = True
            else:
                request.session.pop('remember_me', None)
            return redirect('/')
        else:
            messages.error(request, ("You did not sign in correctly."))
            return redirect('/auth')
    else:
        remember_me = request.session.get('remember_me', False)
        if remember_me:
            username = request.session.get('username', '')
            password = request.session.get('password', '')
            return render(request, 'auth/sign_in.html', {'username': username, 'password': password})
        else:
            return render(request, 'auth/sign_in.html', {})
