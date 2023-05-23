from datetime import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from Schedule.forms import AnnouncementForm
from Schedule.models import Season


def SeasonDetailView(request, *args, **kwargs):
    """
    Displays schedule matches for the season with match result.
    """
    season_qs = Season.objects.all().prefetch_related(
        "divisions",
        "divisions__area",
    )
    if "season_number" in request.GET.keys():
        # If the season number is in the URL, use that season
        season_query = request.GET.get("season_number")
        season = season_qs.filter(season_number=season_query).first()
    else:
        season = Season.objects.latest("match_play_start_dt")

    matches = Season.details.schedule().filter(id=season.id)

    active_div_list = season.divisions.all()  # Get all divisions for the season
    divisions = None  # Get all divisions for the season

    if "division" in request.GET.keys():
        # If the division is in the URL, filter the matches by that division
        division = request.GET.get("division")
        matches = matches.filter(division=division)
        divisions = active_div_list.get(id=division)

    context = {
        "season": season,
        "matches": matches,
        "active_divisions": active_div_list,
        "divisions": divisions,
    }

    return render(request, "schedule/season_detail.html", context)


def MatchDetail(request, season_number, matchID):
    return render(request, "schedule/match_details.html", {})


@permission_required(["Schedule.create_announcement"], raise_exception=True)
def create_announcement_form(request):
    form = AnnouncementForm(request.POST or None)
    context = {"form": form}
    return render(request, "schedule/partials/announcement_form.html", context)


@login_required
@permission_required(
    ["Schedule.create_match", "Schedule.create_scheduleweek", "Schedule.create_season"],
    raise_exception=True,
)
def MatchCreationView(request):
    season = Season.objects.latest()
    active_divisions = season.divisions.all()

    if request.method == "POST":
        for division in active_divisions:
            datetime.strptime(request.POST.get(f"{division.id}"), "%w")


#    for division in active_divisions:
