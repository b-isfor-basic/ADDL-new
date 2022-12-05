from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required

from .models import Player
from .forms import PlayerCreationForm, PlayerChangeForm


@login_required
def PlayerProfileView(request):
    context = {"message": "This is the profile page view."}
    return render(request, "members/playerprofile.html", context)


class PlayerCreateView(CreateView):
    model = Player
    template_name = "members/playercreate.html"
    form_class = PlayerCreationForm