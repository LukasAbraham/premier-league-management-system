from django.urls import path, include
from . import views

app_name = 'home'
urlpatterns = [
    path('', views.index),
    path('auth/', include('apps.auth.urls')),
    path('clubs/', include('apps.clubs.urls')),
    path('players/', include('apps.players.urls')),
]
