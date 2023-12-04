from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

app_name = 'managers'
urlpatterns = [
    path('', views.index, name='index'),
    path('add', views.add, name='add'),
    path('view/<int:manager_id>/', views.view, name='view'),
    path('edit/<int:manager_id>/', views.edit, name='edit'),
    path('delete/<int:manager_id>/', views.delete, name='delete'),
    path('search/', views.search, name='search'),
    path('auth/', include('apps.auth.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
