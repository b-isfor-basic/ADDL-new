from django.contrib import admin
from .models import Season, Match

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'startDate', 'endDate', 'is_active']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['weekNum', 'matchDate', 'division', 'awayTeam', 'homeTeam']
