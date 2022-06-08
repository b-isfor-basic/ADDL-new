import calendar
from calendar import HTMLCalendar

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Season, Match
from Locations.models import Establishment, Division


current_season = Season.objects.first().seasonNum

def SeasonDetailView(request, seasonNum=current_season):
    season = Season.objects.get(seasonNum=seasonNum)
    divisions = season.division_set.all()
    matches = season.match_set.all()
    context = {
        'season': season,
        'matches': matches,
        'divisions': divisions
    }
    return render(request, 'season_detail.html', context)

def SeasonCalendar(request, year, month):
    
    month = month.Title()

    context = {
        'year': year,
        'month': calendar.month_name(month).index(),
    }
    return render(request, 'season_calendar.html', context)


def MatchDetail(request, seasonNum, matchID):
    return render(request, 'match_details.html', {})

@login_required
def MatchCreationView(request):
    pass