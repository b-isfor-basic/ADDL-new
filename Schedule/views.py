import calendar
from calendar import HTMLCalendar

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Now

from .models import Season, Match, Announcement
from Locations.models import Establishment, Division
from .forms import AnnouncementForm, SeasonForm





def SeasonDetailView(request, *division):
    current_season = Season.objects.first().seasonNum
    season = Season.objects.get(seasonNum=current_season)
    if division:
        division = division.id
        matches = Division.objects.get(id=division).match_set.all()
    else:
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


def AnnouncementList(request):
    announcement_list = Announcement.objects.filter(inactive_date__gt=Now())
    return render(request, 'index.html', {'announcement_list': announcement_list})


@login_required
def create_announcement_form(request):
    form = AnnouncementForm(request.POST or None)
    context = {
        "form": form
    }
    return render(request, 'partials/announcement_form.html', context)


@login_required
def MatchCreationView(request):
    season = Season.objects.first()
    active_divisions = season.division_set.all()
    for division in active_divisions:
        division['num_teams']= division.team_set.count()