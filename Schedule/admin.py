from django.contrib import admin
from .models import Season, Match, Announcement

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'startDate', 'endDate']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['weekNum', 'matchDate', 'division', 'awayTeam', 'homeTeam']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_filter = ('season', 'created_by')
    list_display = ['title', 'created_by', 'active_date', 'inactive_date']