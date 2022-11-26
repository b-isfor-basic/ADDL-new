from django.contrib import admin
from .models import Scoreset, GameScore, Approval


@admin.register(Scoreset)
class ScoresetAdmin(admin.ModelAdmin):
    list_filter = ["match__season", "match__division", "team", "player"]
    list_display = ["team", "player"]


@admin.register(GameScore)
class GameScoreAdmin(admin.ModelAdmin):
    list_filter = [
        "scoreset__match__season",
        "scoreset__player",
        "scoreset__match__division",
        "scoreset__match__weekNum",
    ]
    list_display = [
        "player_display",
        "game_point",
        "stars",
        "perfects",
        "darts_thrown",
        "score_left",
        "in_thrown",
        "out_thrown",
    ]


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_filter = ["match__division", "match__weekNum", "approved"]
    list_display = ["match", "approved", "approved_by"]
