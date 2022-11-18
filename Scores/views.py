from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms import all_valid, formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render

from Members.models import Player
from Schedule.models import Match, Season

from .forms import GameScoreForm, ScoresetForm
from .models import GameScore, Scoreset

ScoresetFormSet = formset_factory(ScoresetForm, extra=2, min_num=2, max_num=2)
GameScoreFormSet = formset_factory(GameScoreForm, extra=10, min_num=0, max_num=10)


@login_required
def ScoresheetCreateView(request, id, **kwargs):
    match = Match.objects.get(id=id)
    home_player_forms = ScoresetFormSet(prefix='home', initial=[{'match': match}])
    away_player_forms = ScoresetFormSet(prefix='away', initial=[{'match': match}])

    away_0_game = GameScoreFormSet(prefix='away_0_game')
    away_1_game = GameScoreFormSet(prefix='away_1_game')
    home_0_game = GameScoreFormSet(prefix='home_0_game')
    home_1_game = GameScoreFormSet(prefix='home_1_game')
        
    if request.method == "POST":
        home_player_forms = ScoresetFormSet(request.POST, prefix='home', initial=[{'match': match}])
        away_player_forms = ScoresetFormSet(request.POST, prefix='away', initial=[{'match': match}])

        away_0_game = GameScoreFormSet(request.POST, prefix='away_0_game')
        away_1_game = GameScoreFormSet(request.POST, prefix='away_1_game')
        home_0_game = GameScoreFormSet(request.POST, prefix='home_0_game')
        home_1_game = GameScoreFormSet(request.POST, prefix='home_1_game')

        if all_valid(formsets=[home_player_forms, away_player_forms, away_0_game, away_1_game, home_0_game, home_1_game]):
            game_score_forms = [away_0_game, away_1_game, home_0_game, home_1_game]
            
            # Create list to hold new scoreset ids to apply GameScores under
            player_scores = []
                        
            for form in away_player_forms.forms:
                away_score = Scoreset.details.create_new(
                    match=match, 
                    team=match.awayTeam, 
                    player=form.cleaned_data['player']
                )
                away_score.save()
                player_scores.append(away_score.id)
            
            for form in home_player_forms.forms:
                home_score = Scoreset.details.create_new(                    
                    match=match, 
                    team=match.homeTeam, 
                    player=form.cleaned_data['player']
                ) 
                home_score.save()
                player_scores.append(home_score.id)

            for form_set in game_score_forms: # Loop through each player
                for i in range(10): # Loop through each game
                    
                    # Create singles cricket scores
                    while i < 2:
                        form = form_set.forms[i]
                        scoreset = Scoreset.objects.get(id=player_scores[form_set.index])
                        stars = form.cleaned_data['stars']
                        perfects = form.cleaned_data['perfects']
                        game_point = form.cleaned_data['game_point']
                        new_score = GameScore.singles_cricket.create(
                            scoreset=scoreset,
                            stars=stars,
                            perfects=perfects,
                            game_point=game_point
                        )
                        new_score.save()
               
                    # Create doubles cricket scores
                    while i >= 2 and i < 4:
                        form = form_set.forms[i]
                        scoreset = Scoreset.objects.get(id=player_scores[form_set.index])
                        stars = form.cleaned_data['stars']
                        perfects = form.cleaned_data['perfects']
                        game_point = form.cleaned_data['game_point']
                        new_score = GameScore.doubles_cricket.create(
                            scoreset=scoreset,
                            stars=stars,
                            perfects=perfects,
                            game_point=game_point
                        )
                        new_score.save()
                
                    # Create singles 501 scores
                    while i >= 4 and i < 6:
                        form = form_set.forms[i]
                        scoreset = Scoreset.objects.get(id=player_scores[form_set.index])
                        stars = form.cleaned_data['stars']
                        perfects = form.cleaned_data['perfects']
                        game_point = form.cleaned_data['game_point']
                        out_thrown = form.cleaned_data['out_thrown']
                        darts_thrown = form.cleaned_data['darts_thrown']
                        score_left = form.cleaned_data['score_left']
                        new_score = GameScore.singles_501.create(
                            scoreset=scoreset,
                            stars=stars,
                            perfects=perfects,
                            game_point=game_point,
                            out_thrown=out_thrown,
                            darts_thrown=darts_thrown,
                            score_left=score_left
                        )
                        new_score.save()
                
                    # Create doubles 301 scores
                    while i >= 6 and i < 8:
                        form = form_set.forms[i]
                        scoreset = Scoreset.objects.get(id=player_scores[form_set.index])
                        stars = form.cleaned_data['stars']
                        perfects = form.cleaned_data['perfects']
                        game_point = form.cleaned_data['game_point']
                        out_thrown = form.cleaned_data['out_thrown']
                        in_thrown = form.cleaned_data['in_thrown']
                        new_score = GameScore.doubles_301.create(
                            scoreset=scoreset,
                            stars=stars,
                            perfects=perfects,
                            game_point=game_point,
                            out_thrown=out_thrown,
                            in_thrown=in_thrown
                        )
                        new_score.save()

                    # Create doubles 501 scores
                    while i >= 8:
                        form = form_set.forms[i]
                        scoreset = Scoreset.objects.get(id=player_scores[form_set.index])
                        stars = form.cleaned_data['stars']
                        perfects = form.cleaned_data['perfects']
                        game_point = form.cleaned_data['game_point']
                        out_thrown = form.cleaned_data['out_thrown']
                        darts_thrown = form.cleaned_data['darts_thrown']
                        score_left = form.cleaned_data['score_left']
                        new_score = GameScore.doubles_501.create(
                            scoreset=scoreset,
                            stars=stars,
                            perfects=perfects,
                            game_point=game_point,
                            out_thrown=out_thrown,
                            darts_thrown=darts_thrown,
                            score_left=score_left
                        )
                        new_score.save()

            return HttpResponseRedirect('/schedule/')
        
        else:
            print('home_player_forms ', home_player_forms.errors)
            print('away_player_forms ', away_player_forms.errors)
            print('away_0 ', away_0_game.errors)
            print('away_1 ', away_1_game.errors)
            print('home_0 ', home_0_game.errors)
            print('home_1 ', home_1_game.errors)

    context = {
        'match': match,
        'home_player_forms': home_player_forms,
        'away_player_forms': away_player_forms,
        'away_0_game': away_0_game,
        'away_1_game': away_1_game,
        'home_0_game': home_0_game,
        'home_1_game': home_1_game,       
    }

    return render(request, 'scores/add_scoresheet.html', context)

 
def StandingsView(request, season=Season.objects.first(), *args, **kwargs):
    season = season
    
    matches = season.match_set.all()
    context = {
        'season': season,
        #'matches': matches
    }
    return render(request, 'scores/standings.html', context)


def PlayerSearchView(request, **kwargs):
    template = 'scores/partials/player_search.html'

    if 'player' in request.GET.keys():  
        qs = request.GET.get('player')    
        object_list = Player.objects.filter(
            Q(first_name__icontains=qs)| 
            Q(last_name__icontains=qs)|
            Q(username__icontains=qs)|
            Q(email__icontains=qs)
        )
        context = {
            'object_list': object_list
        }
        return render(request, template, context)
    else:
        return None