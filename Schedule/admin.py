from django.contrib import admin
from .models import Season, Match, Announcement, Scheduler


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ["season_number", "match_play_start_dt", "match_play_end_dt"]


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_filter = ["season", "division"]
    list_display = [
        "weekNum",
        "matchDate",
        "division",
        "awayTeam",
        "homeTeam",
    ]


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_filter = ["created_by"]
    list_display = ["title", "created_by", "active_date", "inactive_date"]


@admin.register(Scheduler)
class RecurringEventAdmin(admin.ModelAdmin):
    list_display = ["title"]
