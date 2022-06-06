from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required

from Schedule.models import Match
# from .models import PlayerStats, TeamStats
#from .forms import Scoresheet

@login_required
def ScoresheetCreateView(request, pk):
    match = Match.objects.get(id=pk)
#    form = Scoresheet(request.POST or None, instance=[PlayerScore, TeamScore])
    
#    if request.method == "POST":
#        if form.is_valid():
#            pass
