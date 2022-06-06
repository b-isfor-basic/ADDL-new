from django.urls import path
from . import views

urlpatterns = [
    path('', views.ScheduleView, name='schedule')
]