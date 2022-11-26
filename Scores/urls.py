from django.urls import path, re_path

from .views import *

urlpatterns = [
    path("add/<uuid:id>", ScoresheetCreateView, name="add_scoresheet"),
    path("", StandingsView, name="standings"),
    re_path(r"^(?P<query>\w+)/$", StandingsView, name="standings"),
    #    path('mystats/<int:season_id>/', views.PersonalStatsView, name='my_stats'),
]
