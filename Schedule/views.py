from django.shortcuts import render

from .models import Season, Match
from Locations.models import Establishment, Division


def ScheduleView(request):
    season = Season.objects.first()
    divisions = Division.objects.all()
    # matches = Season.matches_set.all()
    context = {
        'season': season,
    #    'matches': matches,
        'divisions': divisions
    }
    return render(request, 'season_calendar.html', context)