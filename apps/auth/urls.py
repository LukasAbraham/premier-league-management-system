from django.urls import path
from . import views

app_name = 'auth'
urlpatterns = [
    path('logout', views.logout_user, name='logout'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('', views.sign_in, name='sign_in')
]
