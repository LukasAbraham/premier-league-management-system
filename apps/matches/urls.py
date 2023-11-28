from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

app_name = 'matches'
urlpatterns = [
    path('', views.index, name='index'),
    path('add', views.add, name='add'),
    path('result/add/<int:match_id>/', views.add_result, name='add_result'),
    path('goal_events/add/<int:match_id>/', views.add_goal_events, name='add_goal_events'),
    path('view/<int:match_id>/', views.view, name='view'),
    path('edit/<int:match_id>/', views.edit, name='edit'),
    path('delete/<int:match_id>/', views.delete, name='delete'),
    path('auth/', include('apps.auth.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)