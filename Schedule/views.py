from datetime import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.db.models import F, Sum, Q, Case, When, Value
from django.db.models.lookups import GreaterThan, LessThanOrEqual

from .forms import AnnouncementForm
from .models import Season, ScheduleWeek


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
        season = season_qs.filter(season=request.GET.get("season"))
    else:
        season = season_qs.latest("match_play_start_dt")

    # Get all divisions for the season
    active_div_list = season.divisions.all()

    # Get all matches for the season
    matches = (
        active_div_list.annotate(
            away_sngl_pts=Sum(
                "scheduleweek__match__scoresummary__singles_points",
                filter=Q(
                    scheduleweek__match__scoresummary__team=F(
                        "scheduleweek__match__awayTeam"
                    )
                ),
                distinct=True,
                default=0,
            ),
            away_dbls_pts=Sum(
                "scheduleweek__match__scoresummary__doubles_points",
                filter=Q(
                    scheduleweek__match__scoresummary__team=F(
                        "scheduleweek__match__awayTeam"
                    )
                ),
                distinct=True,
                default=0,
            ),
            home_sngl_pts=Sum(
                "scheduleweek__match__scoresummary__singles_points",
                filter=Q(
                    scheduleweek__match__scoresummary__team=F(
                        "scheduleweek__match__homeTeam"
                    )
                ),
                distinct=True,
                default=0,
            ),
            home_dbls_pts=Sum(
                "scheduleweek__match__scoresummary__doubles_points",
                filter=Q(
                    scheduleweek__match__scoresummary__team=F(
                        "scheduleweek__match__homeTeam"
                    )
                ),
                distinct=True,
                default=0,
            ),
            away_pts=F("away_sngl_pts") + F("away_dbls_pts"),
            home_pts=F("home_sngl_pts") + F("home_dbls_pts"),
        )
        .annotate(
            winner=Case(
                When(GreaterThan(F("away_pts"), F("home_pts")), then=Value("Away")),
                When(GreaterThan(F("home_pts"), F("away_pts")), then=Value("Home")),
                When(
                    GreaterThan(0, (F("home_pts") + F("away_pts"))), then=Value("Draw")
                ),
                default=Value("Missing"),
            )
        )
        .order_by("area__number")
    )
    divisions = active_div_list  # variable required to populate the table

    if "division" in request.GET.keys():
        # If the division is in the URL, filter the matches by that division
        division = request.GET.get("division")
        matches = matches.get(id=division)
        divisions = active_div_list.filter(id=division)

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
