from Locations.models import Division
from Schedule.models import Season


def latest_season(request):
    return {"latest_season": Season.objects.latest("match_play_start_dt").season_number}


def active_divisions(request):
    season = Season.objects.latest("match_play_start_dt")
    return {"active_divisions": Division.objects.filter(season=season)}