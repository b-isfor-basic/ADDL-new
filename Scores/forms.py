from django import forms
from django.contrib.auth.models import User

from Members.models import Team
from Schedule.models import Match

class BaseStats(forms.Form):
    stars = forms.IntegerField(min_value=0)
    perfects = forms.IntegerField(min_value=0)
    win = forms.CheckboxInput()

class Three01(forms.Form):
    in_thrown = forms.IntegerField(required=False, min_value=2, max_value=170)
    out_thrown = forms.IntegerField(required=False, min_value=2, max_value=170)

class Five01(forms.Form):
    darts_thrown = forms.IntegerField(min_value=0)
    points_left = forms.IntegerField(min_value=0, max_value=501)
    out_thrown = forms.IntegerField(min_value=2, max_value=170, required=False)

class SglsGame(forms.Form):
    player = forms.ModelChoiceField(User)

class DblsGame(forms.Form):
    team = forms.ModelChoiceField(Team)

class Scoresheet(forms.Form):
    match = forms.ModelChoiceField(Match)


#    singles_points = forms.IntegerField(min_value=0, max_value=4)
#    doubles_points = forms.IntegerField(min_value=0, max_value=6)