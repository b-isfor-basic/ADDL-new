from django.urls import path, re_path

from .views import *

urlpatterns = [
    path("add/<uuid:id>", CreateScoreSummaryView, name="add_scoresheet"),
    path("", StandingsView, name="standings"),
    #    path('mystats/<int:season_id>/', views.PersonalStatsView, name='my_stats'),
]
