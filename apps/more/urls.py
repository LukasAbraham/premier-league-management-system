from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

app_name = 'more'
urlpatterns = [
    path('', views.index),
    path('regulation/edit/', views.edit_regulation, name='edit_regulation'),
    path('standing', views.standing, name='standing'),
    path('stats_records', views.stats_records, name='stats_records'),
    path('regulation/view/', views.view_regulation, name='view_regulation'),
    path('report', views.report, name='report'),
    path('export_pdf/', views.export_to_pdf, name='export_pdf'),
    path('auth/', include('apps.auth.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)