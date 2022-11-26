from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Player


@login_required
def PlayerProfileView(request):
    context = {"message": "This is the profile page view."}
    return render(request, "members/playerprofile.html", context)
