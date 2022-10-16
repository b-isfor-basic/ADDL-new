from django import forms
from django.forms import Form

from .models import GameScore, Scoreset


class ScoresetForm(forms.ModelForm):
    class Meta:
        model = Scoreset
        fields = ['player']
        widgets = {
            'player': forms.widgets.TextInput(
            )
        }
        
        

class GameScoreForm(forms.ModelForm):
    class Meta:
        model = GameScore
        fields = [
            'stars', 
            'perfects', 
            'game_point',
            'in_thrown',
            'out_thrown', 
            'darts_thrown', 
            'score_left'
        ]
        widgets = {
            'stars': forms.widgets.NumberInput(
                attrs={'class': 'ss-left', 'placeholder': 'stars'}
            ),
            'perfects': forms.widgets.NumberInput(
                attrs={'class': 'ss-center', 'placeholder': 'perfects'}
            ),
            'in_thrown': forms.widgets.NumberInput(
                attrs={'class': 'ss-center', 'placeholder': 'in'}
            ),
            'out_thrown': forms.widgets.NumberInput(
                attrs={'class': 'ss-center', 'placeholder': 'out'}
            ),
            'darts_thrown': forms.widgets.NumberInput(
                attrs={'class': 'ss-center', 'placeholder': 'thrown'}
            ),
            'score_left': forms.widgets.NumberInput(
                attrs={'class': 'ss-right', 'placeholder': 'left'}
            )
        }
    

class CricketForm(forms.ModelForm):
    class Meta:
        model = GameScore
        fields = {
            'stars',
            'perfects',
            'game_point' 
        }
    
class SinglesCricketGameFormset(forms.BaseModelFormSet):
    pass



