from django.urls import path

from .views import *

urlpatterns = [
    path("add/<uuid:id>", CreateScoreSummaryView, name="add_scoresheet"),
    path("edit/<uuid:id>", EditScoreSummaryView, name="edit_scoresheet"),
    path("season/<int:season_number>/division/<int:division_id>", StandingsView, name="standings"),
    path("season/<int:season_number>", StandingsView, name="standings"),
    #    path('mystats/<int:season_id>/', views.PersonalStatsView, name='my_stats'),
]
