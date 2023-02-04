from django.contrib import admin

from .models import ScoreDetail, ScoreSummary, TeamScoreSummary


@admin.register(ScoreSummary)
class ScoreSummaryAdmin(admin.ModelAdmin):
    list_filter = ["match__division", "match__weekNum"]
    list_display = [
        "team",
        "player",
        "total_points",
        "total_stars",
        "total_perfects",
        "high_in",
        "high_out",
        "singles_weekly_ppd",
    ]


@admin.register(ScoreDetail)
class ScoreDetailAdmin(admin.ModelAdmin):
    list_filter = ["match__division", "match__weekNum"]
    list_display = ["team", "player"]


@admin.register(TeamScoreSummary)
class TeamScoreSummaryAdmin(admin.ModelAdmin):
    list_filter = ["match__division", "match__weekNum"]
    list_display = ["team", "weekly_ppd"]
