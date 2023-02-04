from django.contrib import admin
from .models import Season, Match, Announcement, Scheduler, ScheduleWeek


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ["season_number", "match_play_start_dt", "match_play_end_dt"]


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_filter = ["week__season", "week__division", "week__week_number"]
    list_display = [
        "awayTeam",
        "homeTeam",
        "boards"
    ]
    

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_filter = ["created_by"]
    list_display = ["title", "created_by", "active_date", "inactive_date"]


@admin.register(Scheduler)
class RecurringEventAdmin(admin.ModelAdmin):
    list_display = ["title"]


class MatchInline(admin.TabularInline):
    model = Match
    extra = 5
    


@admin.register(ScheduleWeek)
class ScheduleWeekAdmin(admin.ModelAdmin):
    list_filter = ["season", "division"]
    list_display = ["season", "week_number", "division", "playoff_week"]

    inlines = [MatchInline]