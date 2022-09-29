from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('profile', PlayerProfileView, name='profile'),
    re_path(r'^player-autocomplete/$', PlayerAutocomplete.as_view(), name='player-autocomplete')
]
