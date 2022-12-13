from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetCompleteView, 
    PasswordResetConfirmView,
    PasswordResetDoneView,
    LogoutView,
    PasswordResetView,
)

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


class PasswordResetView(PasswordResetView):
    template_name = "registration/password_reset_form.html"
    success_url = "members/password_reset_done"


class PasswordResetDoneView(PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


class PasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"
    success_url = "members/password_reset_complete"