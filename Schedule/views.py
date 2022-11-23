import calendar
from calendar import HTMLCalendar

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.functions import Now

from .models import Season, Match, Announcement
from Locations.models import Establishment, Division
from .forms import AnnouncementForm, SeasonForm





def SeasonDetailView(request, *args, **kwargs):
    season = Season.details.get_active()
    active_div_list = season.division_set.all()
    
    if 'division' in request.GET.keys():
        division = request.GET['division']
        matches = Season.active.matches()
        divisions = season.division_set.get(id=division)
    else:
        matches = season.match_set.all()
        divisions = season.division_set.all()
    
    context = {
        'season': season,
        'matches': matches,
        'active_divisions': active_div_list,
        'divisions': divisions
    }

    return render(request, 'schedule/season_detail.html', context)

def SeasonCalendar(request, year, month):
    
    month = month.Title()

    context = {
        'year': year,
        'month': calendar.month_name(month).index(),
    }
    return render(request, 'schedule/season_calendar.html', context)


def MatchDetail(request, season_number, matchID):
    return render(request, 'schedule/match_details.html', {})


def AnnouncementList(request):
    announcement_list = Announcement.objects.filter(inactive_date__gt=Now())
    return render(request, 'index.html', {'announcement_list': announcement_list})


@login_required
def create_announcement_form(request):
    form = AnnouncementForm(request.POST or None)
    context = {
        "form": form
    }
    return render(request, 'schedule/partials/announcement_form.html', context)


@login_required 
@permission_required
def MatchCreationView(request):
    season = Season.objects.latest()
    active_divisions = season.division_set.all()
#    for division in active_divisions:
        