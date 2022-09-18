from django.urls import path
from . import views

urlpatterns = [
    path('add/<uuid:id>', views.ScoresheetCreateView, name='add_scoresheet'),
    path('mystats/<int:season_id>/', views.PersonalStatsView, name='my_stats'),
]