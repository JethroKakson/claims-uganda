from django.urls import path
from . import views

urlpatterns = [
    path('', views.reminders, name='reminders'),
    path('pause_reminder/', views.pause_reminder, name='pause_reminder'),
    path('resume_reminder/', views.resume_reminder, name='resume_reminder'),
    path('change_stoppage_date/', views.change_stoppage_date, name='change_stoppage_date'),
]