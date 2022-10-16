from django.urls import path
from .views import *

urlpatterns = [
    path('profile', PlayerProfileView, name='profile'),
]
