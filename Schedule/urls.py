from django.urls import path, re_path
from . import views

urlpatterns = [
    path("season/<int:season_number>/", views.SeasonDetailView, name="schedule"),
    path("", views.SeasonDetailView, name="schedule"),
    #re_path(r"^(?P<query>\w+)/$", views.SeasonDetailView, name="schedule"),
]
