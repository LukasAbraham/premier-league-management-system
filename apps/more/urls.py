from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
urlpatterns = [
    path('', views.index),
    path('logout', views.logout_user, name='logout'),
    path('regulation/edit/', views.edit_regulation, name='edit_regulation'),
    path('standing', views.standing, name='standing'),
    path('stats_records', views.stats_records, name='stats_records'),
    path('regulation/view/', views.view_regulation, name='view_regulation'),
    path('report', views.report, name='report'),
    path('export_pdf/', views.export_to_pdf, name='export_pdf'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)