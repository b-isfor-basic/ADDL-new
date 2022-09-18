from django import forms

from dal import autocomplete

from .models import GameScore, Scoreset


class ScoresetForm(forms.ModelForm):
    class Meta:
        model = Scoreset
        fields = ['player']
        widgets = {
            'player': autocomplete.ModelSelect2(
                url='members/player-autocomplete',
                attrs={
                    'data-placeholder': 'Select Player...',
                    'data-minimum-input-length': 3,
                }
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
    
    



