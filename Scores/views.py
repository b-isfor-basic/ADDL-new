from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.forms import all_valid, formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, FormView

from Locations.models import Division
from Members.models import Player
from Schedule.models import Match, Season

from .forms import GameScoreForm, ScoresetForm, PlayerScoreFormSet, TeamScoreFormSet
from .models import GameScore, Scoreset, ScoreSummary, ScoreDetail, TeamScoreSummary

ScoresetFormSet = formset_factory(ScoresetForm, extra=2, min_num=2, max_num=2)
GameScoreFormSet = formset_factory(GameScoreForm, extra=10, min_num=0, max_num=10)


@login_required
def ScoresheetCreateView(request, id, **kwargs):
    match = Match.objects.get(id=id)
    home_player_forms = ScoresetFormSet(prefix="home", initial=[{"match": match}])
    away_player_forms = ScoresetFormSet(prefix="away", initial=[{"match": match}])

    away_0_game = GameScoreFormSet(prefix="away_0_game")
    away_1_game = GameScoreFormSet(prefix="away_1_game")
    home_0_game = GameScoreFormSet(prefix="home_0_game")
    home_1_game = GameScoreFormSet(prefix="home_1_game")

    if request.method == "POST":
        home_player_forms = ScoresetFormSet(
            request.POST, prefix="home", initial=[{"match": match}]
        )
        away_player_forms = ScoresetFormSet(
            request.POST, prefix="away", initial=[{"match": match}]
        )

        away_0_game = GameScoreFormSet(request.POST, prefix="away_0_game")
        away_1_game = GameScoreFormSet(request.POST, prefix="away_1_game")
        home_0_game = GameScoreFormSet(request.POST, prefix="home_0_game")
        home_1_game = GameScoreFormSet(request.POST, prefix="home_1_game")

        if all_valid(
            formsets=[
                home_player_forms,
                away_player_forms,
                away_0_game,
                away_1_game,
                home_0_game,
                home_1_game,
            ]
        ):
            game_score_forms = [away_0_game, away_1_game, home_0_game, home_1_game]

            # Create list to hold new scoreset ids to apply GameScores under
            player_scores = []

            for form in away_player_forms.forms:
                away_score = Scoreset.details.create_new(
                    match=match, team=match.awayTeam, player=form.cleaned_data["player"]
                )
                away_score.save()
                player_scores.append(away_score.id)

            for form in home_player_forms.forms:
                home_score = Scoreset.details.create_new(
                    match=match, team=match.homeTeam, player=form.cleaned_data["player"]
                )
                home_score.save()
                player_scores.append(home_score.id)

            for form_set in game_score_forms:  # Loop through each player
                for i in range(10):  # Loop through each game

                    # Create singles cricket scores
                    while i < 2:
                        form = form_set.forms[i]
                        scoreset = Scoreset.objects.get(
                            id=player_scores[form_set.index]
                        )
                        stars = form.cleaned_data["stars"]
                        perfects = form.cleaned_data["perfects"]
                        game_point = form.cleaned_data["game_point"]
                        new_score = GameScore.singles_cricket.create(
                            scoreset=scoreset,
                            stars=stars,
                            perfects=perfects,
                            game_point=game_point,
                        )
                        new_score.save()

                    # Create doubles cricket scores
                    while i >= 2 and i < 4:
                        form = form_set.forms[i]
                        scoreset = Scoreset.objects.get(
                            id=player_scores[form_set.index]
                        )
                        stars = form.cleaned_data["stars"]
                        perfects = form.cleaned_data["perfects"]
                        game_point = form.cleaned_data["game_point"]
                        new_score = GameScore.doubles_cricket.create(
                            scoreset=scoreset,
                            stars=stars,
                            perfects=perfects,
                            game_point=game_point,
                        )
                        new_score.save()

                    # Create singles 501 scores
                    while i >= 4 and i < 6:
                        form = form_set.forms[i]
                        scoreset = Scoreset.objects.get(
                            id=player_scores[form_set.index]
                        )
                        stars = form.cleaned_data["stars"]
                        perfects = form.cleaned_data["perfects"]
                        game_point = form.cleaned_data["game_point"]
                        out_thrown = form.cleaned_data["out_thrown"]
                        darts_thrown = form.cleaned_data["darts_thrown"]
                        score_left = form.cleaned_data["score_left"]
                        new_score = GameScore.singles_501.create(
                            scoreset=scoreset,
                            stars=stars,
                            perfects=perfects,
                            game_point=game_point,
                            out_thrown=out_thrown,
                            darts_thrown=darts_thrown,
                            score_left=score_left,
                        )
                        new_score.save()

                    # Create doubles 301 scores
                    while i >= 6 and i < 8:
                        form = form_set.forms[i]
                        scoreset = Scoreset.objects.get(
                            id=player_scores[form_set.index]
                        )
                        stars = form.cleaned_data["stars"]
                        perfects = form.cleaned_data["perfects"]
                        game_point = form.cleaned_data["game_point"]
                        out_thrown = form.cleaned_data["out_thrown"]
                        in_thrown = form.cleaned_data["in_thrown"]
                        new_score = GameScore.doubles_301.create(
                            scoreset=scoreset,
                            stars=stars,
                            perfects=perfects,
                            game_point=game_point,
                            out_thrown=out_thrown,
                            in_thrown=in_thrown,
                        )
                        new_score.save()

                    # Create doubles 501 scores
                    while i >= 8:
                        form = form_set.forms[i]
                        scoreset = Scoreset.objects.get(
                            id=player_scores[form_set.index]
                        )
                        stars = form.cleaned_data["stars"]
                        perfects = form.cleaned_data["perfects"]
                        game_point = form.cleaned_data["game_point"]
                        out_thrown = form.cleaned_data["out_thrown"]
                        darts_thrown = form.cleaned_data["darts_thrown"]
                        score_left = form.cleaned_data["score_left"]
                        new_score = GameScore.doubles_501.create(
                            scoreset=scoreset,
                            stars=stars,
                            perfects=perfects,
                            game_point=game_point,
                            out_thrown=out_thrown,
                            darts_thrown=darts_thrown,
                            score_left=score_left,
                        )
                        new_score.save()

            return HttpResponseRedirect("/schedule/")

        else:
            print("home_player_forms ", home_player_forms.errors)
            print("away_player_forms ", away_player_forms.errors)
            print("away_0 ", away_0_game.errors)
            print("away_1 ", away_1_game.errors)
            print("home_0 ", home_0_game.errors)
            print("home_1 ", home_1_game.errors)

    context = {
        "match": match,
        "home_player_forms": home_player_forms,
        "away_player_forms": away_player_forms,
        "away_0_game": away_0_game,
        "away_1_game": away_1_game,
        "home_0_game": home_0_game,
        "home_1_game": home_1_game,
    }

    return render(request, "scores/add_scoresheet.html", context)


def PlayerSearchView(request, **kwargs):
    template = "scores/partials/player_search.html"

    if "player" in request.GET.keys():
        qs = request.GET.get("player")
        object_list = Player.objects.filter(
            Q(first_name__icontains=qs)
            | Q(last_name__icontains=qs)
            | Q(username__icontains=qs)
            | Q(email__icontains=qs)
        ).values("id", "first_name", "last_name", "username", "email")

        context = {"object_list": object_list}
        return render(request, template, context)
    else:
        return None


class StandingsView(ListView):
    model = Scoreset
    template_name = "scores/standings.html"
    context_object_name = "player_stats"
    queryset = Scoreset.player_stats.all()
    season_filter = None
    
    def get_queryset(self, **kwargs):
        if "season" in self.kwargs:
            season = self.kwargs["season"]
            self.season_filter = Season.objects.get(id=season)
            self.division_set = self.season_filter.divisions.all() 
            return Scoreset.player_stats.filter(season=season)
        return super().get_queryset().filter(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context["season_filter"] = self.season_filter or None
        context["all_seasons"] = Season.objects.all()[:5]
        if self.season_filter != None:
            context["season_filter"] = self.season_filter
            context["active_divisions"] = self.division_set
        
        return context
        

class TeamStatsListView(ListView):
    model = Scoreset
    template_name = "scores/team_stats.html"
    context_object_name = "teams"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, **kwargs):
        if kwargs is not None:
            return Scoreset.team_stats.all()
        else:
            return Scoreset.team_stats.filter(**kwargs)


@permission_required("scores.add_score_summary")
def CreateScoreSummaryView(request, id, **kwargs):
    match = Match.objects.get(id=id)
    template = "scores/add_score_summary.html"

    if request.method == "POST":
        team_scores = TeamScoreFormSet(request.POST, prefix="team", form_kwargs={"match": match})
        player_scores = PlayerScoreFormSet(request.POST, prefix="player", form_kwargs={"match": match})

        if team_scores.is_valid() & player_scores.is_valid():
            for form in team_scores:
                form.save()
            for form in player_scores:
                form.save()  
            return HttpResponseRedirect("/schedule/")
        else:
            print("team_scores ", team_scores.errors)
            print("player_scores ", player_scores.errors)
            context = {
                "match": match,
                "team_scores": team_scores,
                "player_scores": player_scores,
            }
    
    team_scores = TeamScoreFormSet(prefix="team", form_kwargs={"match": match})
    player_scores = PlayerScoreFormSet(prefix="player", form_kwargs={"match": match})

    context = {
        "match": match,
        "team_scores": team_scores,
        "player_scores": player_scores,
    }

    return render(request, template, context)
            
    