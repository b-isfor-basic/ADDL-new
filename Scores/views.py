from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory, modelformset_factory

from Schedule.models import Match
from Members.models import Team
from .forms import CricketForm, Three01Form, Five01Form, ScoresetForm, Scoreset


@login_required
def ScoresheetCreateView(request, id):
    match = Match.objects.get(id=id)
    ScoresetFormSet = formset_factory(ScoresetForm, extra=2, min_num=2, max_num=2)
    SnCricketFormSet = formset_factory(CricketForm, extra=8, min_num=8, max_num=8)
    DbCricketFormSet = formset_factory(CricketForm, extra=8, min_num=8, max_num=8)
    Sn501FormSet = formset_factory(Five01Form, extra=8, min_num=8, max_num=8)
    Db501FormSet = formset_factory(Five01Form, extra=8, min_num=8, max_num=8)
    Db301FormSet = formset_factory(Three01Form, extra=8, min_num=8, max_num=8)

        
    if request.method == "POST":
        home_player_forms = ScoresetFormSet(request.POST, prefix='home')
        away_player_forms = ScoresetFormSet(request.POST, prefix='away')

        sn_ckt_forms = SnCricketFormSet(request.POST, prefix='sn_ckt')
        db_ckt_forms = DbCricketFormSet(request.POST, prefix='db_ckt')
        sn_501_forms = Sn501FormSet(request.POST, prefix='sn_501')
        db_301_forms = Db301FormSet(request.POST, prefix='db_301')
        db_501_forms = Db501FormSet(request.POST, prefix='db_501')

        if home_player_forms.is_valid() and away_player_forms.is_valid() and sn_ckt_forms.is_valid() \
        and db_ckt_forms.is_valid() and sn_501_forms.is_valid() and db_301_forms.is_valid() \
        and db_501_forms.is_valid():
            for form in away_player_forms:
                Scoreset.details.create_new(match=match, team=match.awayTeam, player=form.cleaned_data['player'])     
            for form in home_player_forms:
                Scoreset.details.create_new(match=match, team=match.homeTeam, player=form.cleaned_data['player'])     
            return HttpResponseRedirect('/schedule/')
        else:
            away_player_forms = away_player_forms(prefix='away')
            home_player_forms = home_player_forms(prefix='home')
    
    home_player_forms = ScoresetFormSet(prefix='home')
    away_player_forms = ScoresetFormSet(prefix='away')

    context = {
        'match': match,
        'home_player_forms': home_player_forms,
        'away_player_forms': away_player_forms,
       
    }
    
#    if request.method == "POST":
#        if form.is_valid():
#            pass
    return render(request, 'scores/add_scoresheet.html', context)


    def cricket_score_create(request, match_id):
        match = Match.objects.get(id=match_id)
        scoresets = match.scoresets_set.all()
        form = modelformset_factory(GameScoreForm, extra=3) 
