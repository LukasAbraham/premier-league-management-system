from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
urlpatterns = [
    path('', views.index),
    path('logout', views.logout_user, name='logout'),
    path('add', views.add, name='add'),
    path('view/<int:player_id>/', views.view, name='view'),
    path('edit/<int:player_id>/', views.edit, name='edit'),
    path('delete/<int:player_id>/', views.delete, name='delete'),
    path('search/', views.search, name='search'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)