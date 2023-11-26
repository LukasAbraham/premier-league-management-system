from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('logout', views.logout_user, name='logout'),
    path('add', views.add, name='add'),
    path('result/add/<int:match_id>/', views.add_result, name='add_result'),
    path('goal_events/add/<int:match_id>/', views.add_goal_events, name='add_goal_events'),
    path('view/<int:match_id>/', views.view, name='view'),
    path('edit/<int:match_id>/', views.edit, name='edit'),
    path('delete/<int:match_id>/', views.delete, name='delete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)