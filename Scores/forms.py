from django import forms

from dal import autocomplete

from .models import GameScore, Scoreset


class ScoresetForm(forms.ModelForm):
    class Meta:
        model = Scoreset
        fields = ['player']
        # widgets = {
        #     'player': autocomplete.ModelSelect2(
        #         url='player-autocomplete',
        #         attrs={
        #             'data-minimum-input-length': 1,
        #         }
        #     )
        # }
        

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
    
    



