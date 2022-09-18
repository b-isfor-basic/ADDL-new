from math import log as ln

from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max, Min

from Schedule.models import Match, Season
from Locations.models import Division
# from .models import PlayerScore, TeamScore
#from .forms import Scoresheet


@login_required
def PersonalStatsView(request, season_id):
    current_user = request.user.id
    scores = Season.objects.get(pk=season_id).match_set.playerscore_set.filter(player_id=current_user)
    stars = scores.aggregate(Sum('stars'))
    perfects = scores.aggregate(Sum('perfects'))
    singles_wins = scores.aggregate(Sum('singles_points'))
    doubles_wins = scores.aggregate(Sum('doubles_points'))
    total_wins = singles_wins + doubles_wins
    matches_played = scores.count()
    avg_stars_per_game = float(stars / (matches_played * 10))
    win_pct = float(total_wins / (matches_played * 10)) * 100
    high_in = scores.aggregate(Max('high_in'))
    high_out = scores.aggregate(Max('high_out'))
    total_darts_thrown = scores.aggregate(Sum('darts_thrown'))
    total_points_scored =((501 * 2) * matches_played) - scores.aggregate(Sum('score_left'))
    best_week_501 = scores.aggregate(Min('best_501'))
    best_week_ppd = scores.aggregate(Max('weeklyPPD'))
    avg_PPD = total_points_scored / total_darts_thrown
    player_rating = (ln(avg_PPD) * 3.5) + (win_pct * 8) + (avg_stars_per_game * 5)

    

    

@login_required
def ScoresheetCreateView(request, id):
    match = Match.objects.get(id=id)
    context = {
        'match': match,
    }
#    form = Scoresheet(request.POST or None, instance=[PlayerScore, TeamScore])
    
#    if request.method == "POST":
#        if form.is_valid():
#            pass
    return render(request, 'scores/add_scoresheet.html', context)