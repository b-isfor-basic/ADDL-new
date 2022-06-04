from django.contrib import admin
from .models import PlayerScore, TeamScore

admin.site.register([PlayerScore, TeamScore])