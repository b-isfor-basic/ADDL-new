from django import forms
from django.conf import settings
from .models import GameScore

class CricketGameScoreForm(forms.ModelForm):
    
    class Meta:
        model = GameScore
        fields = [
            'scoreset',
            'format',
            'stars',
            'perfects',
            'game_point'
        ]


class Three01GameScoreForm(forms.ModelForm):
    
    class Meta:
        model = GameScore
        fields = [
            "scoreset", 
            'format', 
            'stars', 
            'perfects', 
            'game_point', 
            'in_thrown', 
            'out_thrown'
        ]


class Five01GameScoreForm(forms.ModelForm):
    
    class Meta:
        model = GameScore
        fields = [
            "scoreset", 
            'format', 
            'stars', 
            'perfects', 
            'game_point', 
            'out_thrown', 
            'darts_thrown', 
            'score_left'
        ]

