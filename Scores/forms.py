from django import forms

from .models import GameScore, Scoreset


class ScoresetForm(forms.ModelForm):
    class Meta:
        model = Scoreset
        fields = ['player']
        widgets = {
            'player': forms.widgets.Input()
        }


class SinglesCricketScoreForm(forms.Form):
    '''
    Form for singles cricket matches.
    '''
    away_stars = forms.IntegerField(required=False, min_value=0)
    away_perfects = forms.IntegerField(required=False, min_value=0)
    away_point = forms.IntegerField(min_value=0, max_value=1)
    home_stars = forms.IntegerField(required=False, min_value=0)
    home_perfects = forms.IntegerField(required=False, min_value=0)
    home_point = forms.IntegerField(min_value=0, max_value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        away_point = cleaned_data.get('away_point')
        home_point = cleaned_data.get('home_point')

        # Verify that only one player has a point
        if away_point == home_point:
            raise forms.ValidationError('Invalid score. Only one player can have the game point.')
        
        # Verify that stars are greater than perfects times 3. Perfects = 3 stars.
        for player in ['away', 'home']:
            stars = cleaned_data.get(f'{player}_stars')
            perfects = cleaned_data.get(f'{player}_perfects')
            if stars / 3 < perfects:
                raise forms.ValidationError(f'{player.title()} Stars invalid. Perfects = 3 Stars. Please add 3 Stars to the total Stars per Perfect.')
        
        return cleaned_data
    

class DoublesCricketScoreForm(forms.Form):
    '''
    Form for doubles cricket matches. 
    '''
    # Away Player 1
    away1_stars = forms.IntegerField(required=False, min_value=0)
    away1_perfects = forms.IntegerField(required=False, min_value=0)
    away1_point = forms.IntegerField(min_value=0, max_value=1)
    # Away Player 2
    away2_stars = forms.IntegerField(required=False, min_value=0)
    away2_perfects = forms.IntegerField(required=False, min_value=0)
    away2_point = forms.IntegerField(min_value=0, max_value=1)
    # Home Player 1
    home1_stars = forms.IntegerField(required=False, min_value=0)
    home1_perfects = forms.IntegerField(required=False, min_value=0)
    home1_point = forms.IntegerField(min_value=0, max_value=1)
    # Home Player 2
    home2_stars = forms.IntegerField(required=False, min_value=0)
    home2_perfects = forms.IntegerField(required=False, min_value=0)
    home2_point = forms.IntegerField(min_value=0, max_value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        away1_point = cleaned_data.get('away1_point')
        away2_point = cleaned_data.get('away2_point')
        home1_point = cleaned_data.get('home1_point')
        home2_point = cleaned_data.get('home2_point')

        # Verify that only one team has win points, or that both players on a team have points for winning games
        if away1_point + away2_point == home1_point + home2_point:
            raise forms.ValidationError('Invalid score. Only one team can have the game point.')
        elif away1_point != away2_point | home1_point != home2_point:
            raise forms.ValidationError('Invalid score. Both players on a team must have the same value for game point.')
        
        for player in ['away1', 'away2', 'home1', 'home2']:
            stars = cleaned_data.get(f'{player}_stars')
            perfects = cleaned_data.get(f'{player}_perfects')
            if stars / 3 < perfects:
                raise forms.ValidationError(f'{player.title()} Stars invalid. Perfects = 3 Stars. Please add 3 Stars to the total Stars per Perfect.')
            
        return cleaned_data

            
        
        

    

        

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
            ),
            'game_point': forms.widgets.NumberInput(),
        }
    

class ScoreForm(forms.BaseModelFormSet):    

    class Meta:
        model = GameScore
        fields = {
            'stars',
            'perfects',
            'game_point' 
        }

    def __init__(self, *args, **kwargs):
        super(ScoreForm, self).__init__(*args, **kwargs)
        self.queryset = GameScore.objects.none()
    

                    



