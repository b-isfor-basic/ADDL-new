from django import forms
from django.forms import widgets
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Player


class PlayerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Player
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "email",
            "phoneNumber",
        )


class PlayerChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Player
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "email",
            "phoneNumber",
        )


class PlayerCreationLiteForm(UserCreationForm):
    """
    Form allows for creation of a substitute player.
    Does not require email or password.
    """

    def save(self, commit=True):
        from .models import Player

        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.phoneNumber = self.cleaned_data["phoneNumber"]
        user.username = f"{user.first_name.title()}.{user.last_name.title()}".replace(
            " ", ""
        )
        if Player.objects.exists(username=user.username):
            user.username = f"{user.username}{Player.objects.filter(username=user.username).count()+1}"
        if commit:
            user.save()
        return user

    class Meta(UserCreationForm.Meta):
        model = Player
        fields = ("username", "first_name", "last_name", "phoneNumber")
        widgets = {
            "username": widgets.HiddenInput(),
            "first_name": widgets.TextInput(
                attrs={
                    "class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent",
                }
            ),
            "last_name": widgets.TextInput(
                attrs={
                    "class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent",
                }
            ),
            "phoneNumber": widgets.NumberInput(
                attrs={
                    "class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent",
                    "label": "Phone",
                }
            ),
        }
