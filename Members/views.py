from multiprocessing import context
from django.shortcuts import render

from dal import autocomplete

from Schedule.models import Season, Match
from Scores.models import Scoreset

from .models import Player, Team

def StandingsView(request):
    season = Season.objects.first()
    # matches = season.match_set.all()
    context = {
        'season': season,
    #    'matches': matches
    }
    return render(request, 'scores/standings.html', context)


class PlayerAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Player.objects.none()

        qs = Player.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs