from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('add/<uuid:id>', ScoresheetCreateView, name='add_scoresheet'),
    re_path(r'add/(?P<player>\w+)?', PlayerSearchView, name='player_search'),
    path('', StandingsView, name='standings'),
#    path('mystats/<int:season_id>/', views.PersonalStatsView, name='my_stats'),
]