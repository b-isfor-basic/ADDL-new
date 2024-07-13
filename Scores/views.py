from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.forms import all_valid, modelformset_factory, ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_GET

from Members.models import Player, Team
from Locations.models import Division
from Schedule.models import Match, Season
from Scores.forms import (
    BasePlayerScoreFormSet,
    BaseTeamScoreFormSet,
    PlayerScoreSummaryForm,
    TeamScoreSummaryForm,
)
from Scores.models import ScoreSummary, TeamScoreSummary


LATEST_SEASON = "Season.objects.latest().season_number"


def get_season(season_number):
    if season_number is None:
        season_number = LATEST_SEASON

    return Season.objects.get(season_number=season_number)


def get_latest_seasons(start=None, end=None, qty=None):
    if qty is None:
        qty = 5

    if start is None:
        start = 0
    end = start + qty

    return Season.objects.all()[start:end]


@require_GET
def StandingsView(request, season_number=None, division_id=None, qty=None, **kwargs):
    """
    This view handles displaying stats and standings for a given season. Default is
    the current season. If a division is selected, the standings will be filtered to
    only include that division.
    """
    template = "scores/standings.html"

    season = (
        Season.objects.get(season_number=season_number)
        if season_number
        else Season.objects.latest()
    )
    season_list = get_latest_seasons(qty)
    active_divisions = season.divisions.all()
    division_set = Division.details.filter(season=season.id).get_schedule_weeks()
    teams = Team.stats.filter(season=season.id)
    player_stats = ScoreSummary.stats.filter(match__week__season=season.id)
    player_ratings = ScoreSummary.stats.filter(match__week__season=season.id).rating(
        season=season.id
    )
    team_stats = teams.stats(season=season.id)
    team_standings = teams.weekly_points(season=season.id)

    if division_id is not None:
        division_set = division_set.filter(id=division_id)
        player_stats = player_stats.filter(match__week__division=division_id)
        teams = Team.stats.filter(season=season.id, division_id=division_id)
        team_stats = teams.stats(season=season.id)
        team_standings = team_standings.filter(division__id=division_id)
        player_ratings = player_ratings.filter(match__week__division=division_id)

    context = {
        "season": season,
        "season_list": season_list,
        "active_divisions": active_divisions,
        "division_set": division_set,
        "player_stats": player_stats,
        "team_stats": team_stats,
        "team_standings": team_standings.values(),
        "player_ratings": player_ratings,
    }
    return render(request, template, context)


# @permission_required("scores.add_scoresummary", "scores.add_teamscoresummary", "scores.add_forfeit")
@login_required
def CreateScoreSummaryView(request, id, **kwargs):
    template = "scores/add_score_summary.html"
    match = Match.objects.get(id=id)
    PlayerScoreFormSet = modelformset_factory(
        ScoreSummary,
        form=PlayerScoreSummaryForm,
        formset=BasePlayerScoreFormSet,
        extra=4,
        max_num=4,
    )
    TeamScoreFormSet = modelformset_factory(
        TeamScoreSummary,
        form=TeamScoreSummaryForm,
        formset=BaseTeamScoreFormSet,
        extra=2,
        max_num=2,
    )

    if request.method == "GET":
        if match.forfeit_set.exists():
            team_scores = TeamScoreFormSet(
                prefix="team",
                form_kwargs={"match": match},
                queryset=TeamScoreSummary.objects.filter(match=id)
                .order_by("match__awayTeam", "match__homeTeam")
                .all(),
            )
            player_scores = PlayerScoreFormSet(
                prefix="player",
                form_kwargs={"match": match},
                queryset=ScoreSummary.objects.filter(match=id)
                .order_by("match__awayTeam", "match__homeTeam")
                .all(),
            )
        team_scores = TeamScoreFormSet(
            prefix="team",
            form_kwargs={"match": match},
            queryset=TeamScoreSummary.objects.filter(match=id)
            .order_by("match__awayTeam", "match__homeTeam")
            .all(),
        )
        player_scores = PlayerScoreFormSet(
            prefix="player",
            form_kwargs={"match": match},
            queryset=ScoreSummary.objects.filter(match=id)
            .order_by("match__awayTeam", "match__homeTeam")
            .all(),
        )

    if request.method == "POST":
        team_scores = TeamScoreFormSet(
            request.POST,
            prefix="team",
            form_kwargs={"match": match},
            queryset=TeamScoreSummary.objects.filter(match=id)
            .order_by("match__awayTeam", "match__homeTeam")
            .all(),
        )
        player_scores = PlayerScoreFormSet(
            request.POST, prefix="player", form_kwargs={"match": match}
        )

        if team_scores.is_valid():
            if team_scores[0].cleaned_data.get("mark_as_forfeit") or team_scores[
                1
            ].cleaned_data.get("mark_as_forfeit"):
                team_scores.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    "Scoresheet submitted successfully. Forfeit recorded.",
                )
                return HttpResponseRedirect("/schedule/")
            else:
                all_valid([team_scores, player_scores])
                player_scores.save()
                team_scores.save()
                messages.add_message(
                    request, messages.SUCCESS, "Scoresheet submitted successfully."
                )
                return HttpResponseRedirect("/schedule/")
        else:
            messages.add_message(
                request,
                messages.ERROR,
                "There was an error submitting the scoresheet. Please review the form and try again.",
            )

    context = {
        "match": match,
        "team_scores": team_scores,
        "player_scores": player_scores,
    }

    return render(request, template, context)


@permission_required("players.view_player")
def PlayerSearchView(request, **kwargs):
    template = "scores/partials/player_search.html"

    try:
        q = request.GET.get(**kwargs)["p", "q"]
        qs = Player.objects.filter(
            Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(username__icontains=q)
            | Q(email__icontains=q)
        ).values("id", "first_name", "last_name", "username", "email")

        context = {"players": qs}
        return render(request, template, context)
    except:
        return Player.objects.all().values(
            "id", "first_name", "last_name", "username", "email"
        )
