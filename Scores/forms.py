from django import forms

from .models import GameScore, Scoreset


class CricketForm(forms.ModelForm):
    class Meta:
        model = GameScore
        fields = [
            'stars',
            'perfects',
            'game_point'
        ]


class Three01Form(forms.ModelForm):
    class Meta:
        model = GameScore
        fields = [
            'stars', 
            'perfects', 
            'game_point', 
            'in_thrown', 
            'out_thrown'
        ]


class Five01Form(forms.ModelForm):
    class Meta:
        model = GameScore
        fields = [
            'stars', 
            'perfects', 
            'game_point',
            'out_thrown', 
            'darts_thrown', 
            'score_left'
        ]


class ScoresetForm(forms.ModelForm):
    class Meta:
        model = Scoreset
        fields = ['player']
        





