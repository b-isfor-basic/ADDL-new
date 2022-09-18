from django.contrib import admin
from .models import Scoreset, GameScore

@admin.register(Scoreset)
class ScoresetAdmin(admin.ModelAdmin):
    list_filter = ['match', 'team', 'player']
    list_display = ['team', 'match', 'player']

@admin.register(GameScore)
class GameScoreAdmin(admin.ModelAdmin):
    list_filter = ['scoreset__player', 'scoreset__match']
    list_display = ['player_display', 'game_point', 'stars', 'perfects', 'darts_thrown', 'score_left', 'in_thrown', 'out_thrown']