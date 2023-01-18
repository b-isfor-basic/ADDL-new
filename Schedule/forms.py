from django import forms

from .models import Announcement, Season


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ("title", "body", "active_date", "inactive_date")


class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = (
            "season_number",
            "divisions",
            "match_play_start_dt",
            "match_play_end_dt",
            "playoff_finals_dt",
            "playoffFinalsLocation",
        )

