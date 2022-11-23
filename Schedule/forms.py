from django import forms

from .models import *


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = (
            'title',
            'body',
            'active_date',
            'inactive_date',
            'season'
        )


class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = (
            'season_number',
            'match_play_start_dt',
            'match_play_end_dt',
            'playoff_finals_dt',
            'playoffFinalsLocation'
        )

    


