from multiprocessing import context
from django.shortcuts import render

from Schedule.models import Season, Match
from Scores.models import Scoreset

def StandingsView(request):
    season = Season.objects.first()
    # matches = season.match_set.all()
    context = {
        'season': season,
    #    'matches': matches
    }
    return render(request, 'scores/standings.html', context)