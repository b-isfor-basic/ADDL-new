from django.contrib import admin
from .models import Season, Match, Announcement, RecurringEvent

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['seasonNum', 'startDate', 'endDate']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_filter = ['season', 'division']
    list_display = ['weekNum', 'matchDate', 'division', 'awayTeam', 'homeTeam', 'winner']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_filter = ('season', 'created_by')
    list_display = ['title', 'created_by', 'active_date', 'inactive_date']

@admin.register(RecurringEvent)
class RecurringEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'recurrence']