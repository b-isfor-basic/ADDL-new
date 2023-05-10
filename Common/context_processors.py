
def latest_season(request):
    '''Returns the latest season number.'''
    from Schedule.models import Season

    season = Season.details.latest('match_play_start_dt')
    latest_season = season.season_number
    active_divisions = season.divisions.all()
    return {"latest_season": latest_season, "season": season, "active_divisions": active_divisions}