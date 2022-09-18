from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('', StandingsView, name='standings'),
    re_path(r'^player-autocomplete/$', PlayerAutocomplete.as_view(), name='player-autocomplete')
]
