from django.urls import path

from .views import *

urlpatterns = [
    path("add/<uuid:id>", CreateScoreSummaryView, name="add_scoresheet"),
    path("edit/<uuid:id>", EditScoreSummaryView, name="edit_scoresheet"),
    path("", StandingsView, name="standings"),
    #    path('mystats/<int:season_id>/', views.PersonalStatsView, name='my_stats'),
]
