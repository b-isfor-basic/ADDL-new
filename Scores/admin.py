from django.contrib import admin
from .models import ScoreSummary, ScoreDetail, TeamScoreSummary


@admin.register(ScoreSummary)
class ScoreSummaryAdmin(admin.ModelAdmin):
    list_filter = ["match__week__division", "match__week__week_number"]
    list_display = ["team", "player", "total_points", "singles_weekly_ppd", "total_stars", "avg_stars_per_game", "total_perfects", "win_pct"]


@admin.register(ScoreDetail)
class ScoreDetailAdmin(admin.ModelAdmin):
    list_filter = ["match__week__division", "match__week__week_number"]
    list_display = ["team", "player"]


@admin.register(TeamScoreSummary)
class TeamScoreSummaryAdmin(admin.ModelAdmin):
    list_filter = ["match__week__division", "match__week__week_number"]
    list_display = ["team", "weekly_ppd"]