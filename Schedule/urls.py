from django.urls import path
from . import views

urlpatterns = [
    path("", views.SeasonDetailView, name="schedule"),
    path("?Pdivision=<division>\d/", views.SeasonDetailView, name="schedule"),
    path("<int:season_number>/", views.SeasonDetailView, name="schedule"),
]
