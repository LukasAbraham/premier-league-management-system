from django.urls import path, include
from . import views

app_name = 'home'
urlpatterns = [
    path('', views.index),
    path('auth/', include('apps.auth.urls'))
]
