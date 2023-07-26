from django.contrib import admin

from .models import ScoreDetail, ScoreSummary, TeamScoreSummary


@admin.register(ScoreSummary)
class ScoreSummaryAdmin(admin.ModelAdmin):
    list_filter = [
        "match__week__season",
        "match__week__division",
        "match__week__week_number",
    ]
    list_display = [
        "player",
        "team",
        "singles_weekly_ppd",
        "total_points",
        "total_stars",
        "total_perfects",
    ]
    ordering = [
        "-match__week__season",
        "match__week__week_number",
        "player__first_name",
        "player__last_name",
    ]

    @admin.display(empty_value="None")
    def singles_weekly_ppd(self, obj):
        return obj.singles_weekly_ppd


@admin.register(ScoreDetail)
class ScoreDetailAdmin(admin.ModelAdmin):
    list_filter = [
        "match__week__season",
        "match__week__division",
        "match__week__week_number",
    ]
    list_display = [
        "player",
        "team",
    ]


@admin.register(TeamScoreSummary)
class TeamScoreSummaryAdmin(admin.ModelAdmin):
    list_filter = [
        "match__week__season",
        "match__week__division",
        "match__week__week_number",
    ]
    list_display = [
        "team",
        "weekly_ppd",
    ]
