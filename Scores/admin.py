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
        "total_points",
        "singles_points",
        "doubles_points",
        "darts_thrown1",
        "score_left1",
        "darts_thrown2",
        "score_left2",
        "total_stars",
        "total_perfects",
        "singles_weekly_ppd",
    ]
    ordering = [
        "-match__week__season",
        "match__week__week_number",
        "player__first_name",
        "player__last_name",
    ]
    autocomplete_fields = ["player", "team"]

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


#@admin.register(Forfeit)
#class ForfeitAdmin(admin.ModelAdmin):
#    list_filter = [
#        "match__week__season",
#        "match__week__division",
#        "match__week__week_number",
#    ]
#    list_display = [
#        "week__season",
#
#        "team",
#    ]