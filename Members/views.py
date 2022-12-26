from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)

from .models import Player
from .forms import PlayerCreationForm, PlayerChangeForm


class SuccessMessageMixin(SuccessMessageMixin):
    success_message_template = "components/success.html"

# TODO: This should be limited to only the user who is logged in and not all users.
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
    