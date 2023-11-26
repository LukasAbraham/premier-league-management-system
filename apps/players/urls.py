from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

app_name = 'players'
urlpatterns = [
    path('', views.index),
    path('add', views.add, name='add'),
    path('view/<int:player_id>/', views.view, name='view'),
    path('edit/<int:player_id>/', views.edit, name='edit'),
    path('delete/<int:player_id>/', views.delete, name='delete'),
    path('search/', views.search, name='search'),
    path('auth/', include('apps.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)