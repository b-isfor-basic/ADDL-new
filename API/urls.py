from django.urls import path
from .views import *

urlpatterns = [
    path('players', player_list),
]