from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

app_name = 'clubs'
urlpatterns = [
    path('', views.index),
    path('add', views.add, name='add'),
    path('view/<int:club_id>/', views.view, name='view'),
    path('edit/<int:club_id>/', views.edit, name='edit'),
    path('delete/<int:club_id>/', views.delete, name='delete'),
    path('search/', views.search, name='search'),
    path('players/', include('apps.players.urls')),
    path('managers/', include('apps.managers.urls')),
    path('auth/', include('apps.auth.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)