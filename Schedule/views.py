from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from datetime import datetime


from .forms import AnnouncementForm
from .models import Season


def SeasonDetailView(request, *args, **kwargs):
    season = Season.details.get_active()
    active_div_list = season.divisions.all()

    if "division" in request.GET.keys():
        division = request.GET.get("division")
        matches = season.match_set.filter(division__id=division)
        divisions = season.divisions.get(id=division)
    else:
        matches = season.match_set.all()
        divisions = season.divisions.all()

    context = {
        "season": season,
        "matches": matches,
        "active_divisions": active_div_list,
        "divisions": divisions,
    }

    return render(request, "schedule/season_detail.html", context)


def MatchDetail(request, season_number, matchID):
    return render(request, "schedule/match_details.html", {})


@login_required
def create_announcement_form(request):
    form = AnnouncementForm(request.POST or None)
    context = {"form": form}
    return render(request, "schedule/partials/announcement_form.html", context)


@login_required
@permission_required
def MatchCreationView(request):
    season = Season.objects.latest()
    active_divisions = season.divisions.all()

    if request.method == "POST":
        for division in active_divisions:
            datetime.strptime(request.POST.get(f"{division.id}"), "%w")


#    for division in active_divisions:
