from django import forms

class Game(forms.Form):
    stars = forms.IntegerField(min_value=0)
    perfects = forms.IntegerField(min_value=0)
    win = forms.CheckboxInput()


class Three01(forms.Form):
    in_thrown = forms.IntegerField(required=False, min_value=2, max_value=170)
    out_thrown = forms.IntegerField(required=False, min_value=2, max_value=170)


class Five01(forms.Form):
    darts_thrown = forms.IntegerField(min_value=0)
    points_left = forms.IntegerField(min_value=0, max_value=501)
    out_thrown = forms.IntegerField(min_value=2, max_value=170)


class Scoresheet(forms.Form):
    # Form to combine all stats and create appropriate Score record.
    team = forms.ModelChoiceField('Members.Team')
    player = forms.ModelChoiceField('Members.Player')
    sub = forms.CheckboxInput()
    


#    singles_points = forms.IntegerField(min_value=0, max_value=4)
#    doubles_points = forms.IntegerField(min_value=0, max_value=6)