from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView

from Schedule.models import Match
from .models import PlayerScore, TeamScore

# Create your views here.
def ScoresheetCreateView(request, pk):
    match_result = get_object_or_404(Match, pk=id)
    template_name = "add_scoresheet.html"
