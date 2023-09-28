from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.forms import all_valid, modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, resolve_url
from django.views.decorators.http import require_GET, require_safe
from django.views.generic import UpdateView

from Members.models import Player, Team
from Schedule.models import Match, Season
from Scores.forms import (
    BasePlayerScoreFormSet,
    BaseTeamScoreFormSet,
    PlayerScoreSummaryForm,
    TeamScoreSummaryForm,
)
from Scores.models import ScoreSummary, TeamScoreSummary


LATEST_SEASON = "Season.objects.first().season_number"


def get_season(season_number="Season.objects.first().season_number"):
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


def get_division_filter(season=LATEST_SEASON):
    return season.divisions(manager="details").get_average_rating(season.season_number)


@require_GET
def StandingsView(request, season_number=None, division_id=None, qty=None, **kwargs):
    """
    This view handles displaying stats and standings for a given season. Default is
    the current season. If a division is selected, the standings will be filtered to
    only include that division.
    """
    template = "scores/standings.html"

    season = get_season(season_number)
    season_list = get_latest_seasons(qty)
    division_set = get_division_filter(season)
    active_divisions = (
        season.divisions(manager="details").get_average_rating(season_number).all()
    )

    player_stats = (
        ScoreSummary.stats.filter(match__week__season=season.id)
    )
    team_stats = (
        TeamScoreSummary.stats.filter(match__week__season=season.id)
    )
    team_standings = (
        ScoreSummary.stats.filter(match__week__season=season.id)
        .group_by_teams()
        .total_wins()
    )

    if division_id is not None:
        division_set = division_set.filter(id=division_id)
        player_stats = player_stats.filter(match__week__division=division_id)
        team_stats = team_stats.filter(match__week__division=division_id)
        team_standings = team_standings.filter(match__week__division=division_id)

    context = {
        "season": season,
        "season_list": season_list,
        "active_divisions": active_divisions,
        "division_set": division_set,
        "player_stats": player_stats,
        "team_stats": team_stats,
        "team_standings": team_standings,
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
        queryset=Match.objects.get(id=id).teamscoresummary_set.all(),
    )
    player_scores = PlayerScoreFormSet(
        prefix="player",
        form_kwargs={"match": match},
        queryset=Match.objects.get(id=id).scoresummary_set.all(),
    )

    if request.method == "POST":
        team_scores = TeamScoreFormSet(
            request.POST, prefix="team", form_kwargs={"match": match}
        )
        player_scores = PlayerScoreFormSet(
            request.POST, prefix="player", form_kwargs={"match": match}
        )

        if (
            all_valid([team_scores, player_scores])
            and team_scores.is_valid()
            and player_scores.is_valid()
        ):
            for form in team_scores:
                form.save()
            for form in player_scores:
                form.save()
            messages.add_message(
                request, messages.SUCCESS, "Scoresheet submitted successfully."
            )
            return HttpResponseRedirect("/schedule/")
        else:
            context = {
                "match": match,
                "team_scores": team_scores,
                "player_scores": player_scores,
            }
            messages.add_message(
                request,
                messages.ERROR,
                "There were some issues with your submission. Please review the form and try again.",
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
        q = request.GET.get(**kwargs)["P", "q"]
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


# Former Scoresheet handling logic below. Keeping for reference.

# ScoresetFormSet = formset_factory(ScoresetForm, extra=2, min_num=2, max_num=2)
# GameScoreFormSet = formset_factory(GameScoreForm, extra=10, min_num=0, max_num=10)

# @login_required
# def ScoresheetCreateView(request, id, **kwargs):
#     match = Match.objects.get(id=id)
#     home_player_forms = ScoresetFormSet(prefix="home", initial=[{"match": match}])
#     away_player_forms = ScoresetFormSet(prefix="away", initial=[{"match": match}])

#     away_0_game = GameScoreFormSet(prefix="away_0_game")
#     away_1_game = GameScoreFormSet(prefix="away_1_game")
#     home_0_game = GameScoreFormSet(prefix="home_0_game")
#     home_1_game = GameScoreFormSet(prefix="home_1_game")

#     if request.method == "POST":
#         home_player_forms = ScoresetFormSet(
#             request.POST, prefix="home", initial=[{"match": match}]
#         )
#         away_player_forms = ScoresetFormSet(
#             request.POST, prefix="away", initial=[{"match": match}]
#         )

#         away_0_game = GameScoreFormSet(request.POST, prefix="away_0_game")
#         away_1_game = GameScoreFormSet(request.POST, prefix="away_1_game")
#         home_0_game = GameScoreFormSet(request.POST, prefix="home_0_game")
#         home_1_game = GameScoreFormSet(request.POST, prefix="home_1_game")

#         if all_valid(
#             formsets=[
#                 home_player_forms,
#                 away_player_forms,
#                 away_0_game,
#                 away_1_game,
#                 home_0_game,
#                 home_1_game,
#             ]
#         ):
#             game_score_forms = [away_0_game, away_1_game, home_0_game, home_1_game]

#             # Create list to hold new scoreset ids to apply GameScores under
#             player_scores = []

#             for form in away_player_forms.forms:
#                 away_score = Scoreset.details.create_new(
#                     match=match, team=match.awayTeam, player=form.cleaned_data["player"]
#                 )
#                 away_score.save()
#                 player_scores.append(away_score.id)

#             for form in home_player_forms.forms:
#                 home_score = Scoreset.details.create_new(
#                     match=match, team=match.homeTeam, player=form.cleaned_data["player"]
#                 )
#                 home_score.save()
#                 player_scores.append(home_score.id)

#             for form_set in game_score_forms:  # Loop through each player
#                 for i in range(10):  # Loop through each game

#                     # Create singles cricket scores
#                     while i < 2:
#                         form = form_set.forms[i]
#                         scoreset = Scoreset.objects.get(
#                             id=player_scores[form_set.index]
#                         )
#                         stars = form.cleaned_data["stars"]
#                         perfects = form.cleaned_data["perfects"]
#                         game_point = form.cleaned_data["game_point"]
#                         new_score = GameScore.singles_cricket.create(
#                             scoreset=scoreset,
#                             stars=stars,
#                             perfects=perfects,
#                             game_point=game_point,
#                         )
#                         new_score.save()

#                     # Create doubles cricket scores
#                     while i >= 2 and i < 4:
#                         form = form_set.forms[i]
#                         scoreset = Scoreset.objects.get(
#                             id=player_scores[form_set.index]
#                         )
#                         stars = form.cleaned_data["stars"]
#                         perfects = form.cleaned_data["perfects"]
#                         game_point = form.cleaned_data["game_point"]
#                         new_score = GameScore.doubles_cricket.create(
#                             scoreset=scoreset,
#                             stars=stars,
#                             perfects=perfects,
#                             game_point=game_point,
#                         )
#                         new_score.save()

#                     # Create singles 501 scores
#                     while i >= 4 and i < 6:
#                         form = form_set.forms[i]
#                         scoreset = Scoreset.objects.get(
#                             id=player_scores[form_set.index]
#                         )
#                         stars = form.cleaned_data["stars"]
#                         perfects = form.cleaned_data["perfects"]
#                         game_point = form.cleaned_data["game_point"]
#                         out_thrown = form.cleaned_data["out_thrown"]
#                         darts_thrown = form.cleaned_data["darts_thrown"]
#                         score_left = form.cleaned_data["score_left"]
#                         new_score = GameScore.singles_501.create(
#                             scoreset=scoreset,
#                             stars=stars,
#                             perfects=perfects,
#                             game_point=game_point,
#                             out_thrown=out_thrown,
#                             darts_thrown=darts_thrown,
#                             score_left=score_left,
#                         )
#                         new_score.save()

#                     # Create doubles 301 scores
#                     while i >= 6 and i < 8:
#                         form = form_set.forms[i]
#                         scoreset = Scoreset.objects.get(
#                             id=player_scores[form_set.index]
#                         )
#                         stars = form.cleaned_data["stars"]
#                         perfects = form.cleaned_data["perfects"]
#                         game_point = form.cleaned_data["game_point"]
#                         out_thrown = form.cleaned_data["out_thrown"]
#                         in_thrown = form.cleaned_data["in_thrown"]
#                         new_score = GameScore.doubles_301.create(
#                             scoreset=scoreset,
#                             stars=stars,
#                             perfects=perfects,
#                             game_point=game_point,
#                             out_thrown=out_thrown,
#                             in_thrown=in_thrown,
#                         )
#                         new_score.save()

#                     # Create doubles 501 scores
#                     while i >= 8:
#                         form = form_set.forms[i]
#                         scoreset = Scoreset.objects.get(
#                             id=player_scores[form_set.index]
#                         )
#                         stars = form.cleaned_data["stars"]
#                         perfects = form.cleaned_data["perfects"]
#                         game_point = form.cleaned_data["game_point"]
#                         out_thrown = form.cleaned_data["out_thrown"]
#                         darts_thrown = form.cleaned_data["darts_thrown"]
#                         score_left = form.cleaned_data["score_left"]
#                         new_score = GameScore.doubles_501.create(
#                             scoreset=scoreset,
#                             stars=stars,
#                             perfects=perfects,
#                             game_point=game_point,
#                             out_thrown=out_thrown,
#                             darts_thrown=darts_thrown,
#                             score_left=score_left,
#                         )
#                         new_score.save()

#             return HttpResponseRedirect("/schedule/")

#         else:
#             print("home_player_forms ", home_player_forms.errors)
#             print("away_player_forms ", away_player_forms.errors)
#             print("away_0 ", away_0_game.errors)
#             print("away_1 ", away_1_game.errors)
#             print("home_0 ", home_0_game.errors)
#             print("home_1 ", home_1_game.errors)

#     context = {
#         "match": match,
#         "home_player_forms": home_player_forms,
#         "away_player_forms": away_player_forms,
#         "away_0_game": away_0_game,
#         "away_1_game": away_1_game,
#         "home_0_game": home_0_game,
#         "home_1_game": home_1_game,
#     }

#     return render(request, "scores/add_scoresheet.html", context)
