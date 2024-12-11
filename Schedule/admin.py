from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django import forms

from .models import Announcement, Match, ScheduleWeek, Season
from Members.models import Team


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = [
        "season_number",
        "match_play_start_dt",
        "match_play_end_dt",
    ]
    filter_horizontal = ["divisions"]


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_filter = [
        "week__season",
        "week__division",
        "week__week_number",
    ]
    list_display = ["awayTeam", "awayBye", "homeTeam", "homeBye", "status"]
    search_fields = [
        "awayTeam__players__last_name",
        "homeTeam__players__last_name",
    ]


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_filter = [
        ("created_by", admin.RelatedOnlyFieldListFilter),
        "active_date",
        "inactive_date",
    ]
    list_display = ["title", "created_by", "active_date", "inactive_date"]


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ["awayTeam", "homeTeam"]
        widgets = {
            "awayTeam": AutocompleteSelect(
                Match._meta.get_field("awayTeam"), admin.site
            ),
            "homeTeam": AutocompleteSelect(
                Match._meta.get_field("homeTeam"), admin.site
            ),
        }


class MatchInline(admin.TabularInline):
    model = Match
    form = MatchForm
    extra = 6


@admin.register(ScheduleWeek)
class ScheduleWeekAdmin(admin.ModelAdmin):
    list_filter = ["season", "division"]
    list_display = ["season", "week_number", "division", "playoff_week"]

    inlines = [MatchInline]
