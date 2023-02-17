from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from datetime import datetime


from .forms import AnnouncementForm
from .models import Season, ScheduleWeek


def SeasonDetailView(request, *args, **kwargs):
    season = Season.objects.all().prefetch_related('divisions', 'divisions__team_set').latest('match_play_start_dt')
    active_div_list = season.divisions.all()

    if "division" in request.GET.keys():
        division = request.GET.get("division")
        matches = ScheduleWeek.objects.all().prefetch_related('match_set', 'match_set__scoresummary_set', 'match_set__scoresummary_set__team', 'match_set__awayTeam', 'match_set__awayTeam__players', 'match_set__homeTeam', 'match_set__homeTeam__players').select_related('division').filter(season=season, division=division)
        divisions = season.divisions.get(id=division)
    else:
        matches = ScheduleWeek.objects.all().prefetch_related('match_set', 'match_set__scoresummary_set', 'match_set__scoresummary_set__team', 'match_set__awayTeam', 'match_set__awayTeam__players', 'match_set__homeTeam', 'match_set__homeTeam__players').select_related('division').filter(season=season)
        divisions = season.divisions.all()

    context = {
        "season": season,
        "matches": matches,
        "active_divisions": active_div_list,
        "divisions": divisions,
    }

    return render(request, "schedule/season_detail.html", context)


def MatchDetail(request, season_number, matchID):
    return render(request, "schedule/match_details.html", {})


@login_required
def create_announcement_form(request):
    form = AnnouncementForm(request.POST or None)
    context = {"form": form}
    return render(request, "schedule/partials/announcement_form.html", context)


@login_required
@permission_required
def MatchCreationView(request):
    season = Season.objects.latest()
    active_divisions = season.divisions.all()

    if request.method == "POST":
        for division in active_divisions:
            datetime.strptime(request.POST.get(f"{division.id}"), "%w")


#    for division in active_divisions:
