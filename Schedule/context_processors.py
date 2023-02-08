from .models import Season

def latest_season(request):
    return {"latest_season": Season.objects.latest("match_play_start_dt").season_number}