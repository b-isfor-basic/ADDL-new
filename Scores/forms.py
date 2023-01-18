from django import forms
from django.db.models import Q

from Members.models import Player, Team
from Schedule.models import Match, Season

from .models import GameScore, Scoreset, ScoreSummary, TeamScoreSummary, Forfeit


class ScoresetForm(forms.ModelForm):
    class Meta:
        model = Scoreset
        fields = ["player"]
        widgets = {"player": forms.widgets.Input()}


class SinglesCricketScoreForm(forms.Form):
    """
    Form for singles cricket matches.
    """

    away_stars = forms.IntegerField(required=False, min_value=0)
    away_perfects = forms.IntegerField(required=False, min_value=0)
    away_point = forms.IntegerField(min_value=0, max_value=1)
    home_stars = forms.IntegerField(required=False, min_value=0)
    home_perfects = forms.IntegerField(required=False, min_value=0)
    home_point = forms.IntegerField(min_value=0, max_value=1)

    class Meta:
        fieldsets = {
            "away player": ["away_stars", "away_perfects", "away_point"],
            "home player": ["home_stars", "home_perfects", "home_point"],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        away_point = cleaned_data.get("away_point")
        home_point = cleaned_data.get("home_point")

        # Verify that only one player has a point
        if away_point == home_point:
            raise forms.ValidationError(
                "Invalid score. Only one player can have the game point."
            )

        # Verify that stars are greater than perfects times 3. Perfects = 3 stars.
        for player in ["away", "home"]:
            stars = cleaned_data.get(f"{player}_stars")
            perfects = cleaned_data.get(f"{player}_perfects")
            if stars / 3 < perfects:
                raise forms.ValidationError(
                    f"{player.title()} Stars invalid. Perfects = 3 Stars. Please add 3 Stars to the total Stars per Perfect."
                )

        return cleaned_data


class DoublesCricketScoreForm(forms.Form):
    """
    Form for doubles cricket matches.
    """

    # Away Player 1
    a0_stars = forms.IntegerField(required=False, min_value=0)
    a0_perfects = forms.IntegerField(required=False, min_value=0)
    a0_point = forms.IntegerField(min_value=0, max_value=1)
    # Away Player 2
    a1_stars = forms.IntegerField(required=False, min_value=0)
    a1_perfects = forms.IntegerField(required=False, min_value=0)
    a1_point = forms.IntegerField(min_value=0, max_value=1)
    # Home Player 1
    h0_stars = forms.IntegerField(required=False, min_value=0)
    h0_perfects = forms.IntegerField(required=False, min_value=0)
    h0_point = forms.IntegerField(min_value=0, max_value=1)
    # Home Player 2
    h1_stars = forms.IntegerField(required=False, min_value=0)
    h1_perfects = forms.IntegerField(required=False, min_value=0)
    h1_point = forms.IntegerField(min_value=0, max_value=1)

    class Meta:
        fieldsets = {
            "away-1": ["a0_stars", "a0_perfects", "a0_point"],
            "away-2": ["a1_stars", "a1_perfects", "a1_point"],
            "home-1": ["h0_stars", "h0_perfects", "h0_point"],
            "home-2": ["h1_stars", "h1_perfects", "h1_point"],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean(self)
        a0_point = self.cleaned_data.get("a0_point")
        a1_point = self.cleaned_data.get("a1_point")
        h0_point = self.cleaned_data.get("h0_point")
        h1_point = self.cleaned_data.get("h1_point")

        # Verify that only one team has win points, or that both players on a team have points for winning games
        if a0_point + a1_point == h0_point + h1_point:
            raise forms.ValidationError(
                "Invalid score. Only one team can have a game point."
            )
        elif a0_point != a1_point | h0_point != h1_point:
            raise forms.ValidationError(
                "Invalid score. Both players on a team must have the same score."
            )

        for player in ["a0", "a1", "h0", "h1"]:
            stars = self.cleaned_data.get(f"{player}_stars")
            perfects = self.cleaned_data.get(f"{player}_perfects")
            if stars / 3 < perfects:
                raise forms.ValidationError(
                    f"{player.first_name()} Stars invalid. Perfects = 3 Stars. Please add 3 Stars to the total Stars per Perfect."
                )

        return cleaned_data


class GameScoreForm(forms.ModelForm):
    class Meta:
        model = GameScore
        fields = [
            "stars",
            "perfects",
            "game_point",
            "in_thrown",
            "out_thrown",
            "darts_thrown",
            "score_left",
        ]
        widgets = {
            "stars": forms.widgets.NumberInput(
                attrs={"class": "ss-left", "placeholder": "stars"}
            ),
            "perfects": forms.widgets.NumberInput(
                attrs={"class": "ss-center", "placeholder": "perfects"}
            ),
            "in_thrown": forms.widgets.NumberInput(
                attrs={"class": "ss-center", "placeholder": "in"}
            ),
            "out_thrown": forms.widgets.NumberInput(
                attrs={"class": "ss-center", "placeholder": "out"}
            ),
            "darts_thrown": forms.widgets.NumberInput(
                attrs={"class": "ss-center", "placeholder": "thrown"}
            ),
            "score_left": forms.widgets.NumberInput(
                attrs={"class": "ss-right", "placeholder": "left"}
            ),
            "game_point": forms.widgets.NumberInput(),
        }


class BasePlayerScoreFormSet(forms.BaseModelFormSet):

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        match = kwargs.pop("match")
        if index < 2:
            kwargs.update({'prefix': f'away-player-{index}', 'initial': {"match": match.id, "team": match.awayTeam}})
        else:
            player_num = index - 2
            kwargs.update({'prefix': f'home-player-{player_num}', 'initial': {"match": match.id, "team": match.homeTeam}})
        return kwargs

    def clean(self):
        """
        Verify that the total points does not exceed 20 and that doubles points
        for a team match.
        """
        
        super().clean()

        doubles_pts = []
        total_points = 0
        for form in self.forms:
            singles = form.cleaned_data.get("singles_wins")
            doubles = form.cleaned_data.get("doubles_wins")
            if singles is None:
                singles = 0
            if doubles is None:
                doubles = 0
            total_points += singles + doubles
            doubles_pts.append(doubles)

        if total_points > 20:
            raise forms.ValidationError(
                "Invalid score. Total points for match cannot exceed 20."
            )
                        
        if doubles_pts[0] != doubles_pts[1]:
            raise forms.ValidationError(
                "Invalid score. Both players on a team must have the same doubles score. \
                    Please verify away player 1 and away player 2 scores."
            )
        
        if doubles_pts[2] != doubles_pts[3]:
            raise forms.ValidationError(
                "Invalid score. Both players on a team must have the same doubles score. \
                    Please verify home player 1 and home player 2 scores."
            )
        
        if any(self.errors):
            return

        return self.cleaned_data

class BaseTeamScoreFormSet(forms.BaseModelFormSet):

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        match = kwargs.pop("match")
        if index < 1:
            kwargs.update({'prefix': 'away-team', 'initial': {"match": match.id, "team": match.awayTeam}})
        else:
            kwargs.update({'prefix': 'home-team', 'initial': {"match": match.id, "team": match.homeTeam}})
        return kwargs

    def clean(self):
        """
        Verify that only one team has 0 score left for each game.
        """
        super().clean()
    
        pts_left = []
        for form in self.forms:
            score_left1 = form.cleaned_data.get("score_left1")
            score_left2 = form.cleaned_data.get("score_left2")
            team_pts_left = [score_left1, score_left2]
            pts_left.append(team_pts_left)
        
        for i in list(range(0, 2)):
            if pts_left[0][i] == pts_left[1][i]:
                raise forms.ValidationError(
                    f"Invalid score for Doubles 501 - Game ({str(i)}). \
                        Both teams cannot have the same score left. If the \
                        value is unknown, the winning team should enter 0 \
                        and the losing team should enter 2."
                )
            
        
        if any(self.errors):
            return
        
        return self.cleaned_data


class TeamScoreSummaryForm(forms.ModelForm):
    """
    Summarized match scores for entry by area managers.
    """
    mark_as_forfeit = forms.BooleanField( 
        required=False,
        initial=False,
        widget=forms.widgets.CheckboxInput(
            attrs={"class": "form-checkbox rounded-md h-[18px] w-[18px] text-rose-500 bg-slate-800 border-rose-500 border shadow-slate-900/30 shadow-inner focus:ring-0 focus:outline-none active:text-slate-800"}
        )
    )

    class Meta:
        model = TeamScoreSummary
        fields = [
            "match",
            "team",
            "darts_thrown1",
            "score_left1",
            "darts_thrown2",
            "score_left2",
        ]
        widgets = {
            "match": forms.widgets.HiddenInput(),
            "team": forms.widgets.HiddenInput(),
            "darts_thrown1": forms.widgets.NumberInput(
                attrs={"class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"}
            ),
            "score_left1": forms.widgets.NumberInput(
                attrs={"class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"}
            ),
            "darts_thrown2": forms.widgets.NumberInput(
                attrs={"class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"}
            ),
            "score_left2": forms.widgets.NumberInput(
                attrs={"class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"}
            ),
        }

    def clean(self):
        """
        Verify if the match is being marked as a forfeit.
        """
        super().clean()
        if any(self.errors):
            return

        forfeit = self.cleaned_data.get("mark_as_forfeit")
        if forfeit:
            record = Forfeit.objects.create(
                match=self.cleaned_data.get("match"),
                team=self.cleaned_data.get("team"),
            )
            return record

        return self.cleaned_data


class PlayerScoreSummaryForm(forms.ModelForm):
    """
    Summarized match scores for entry by area managers.
    """
    class Meta:
        model = ScoreSummary
        fields = [
            "match",
            "team",
            "player",
            "darts_thrown1",
            "score_left1",
            "darts_thrown2",
            "score_left2",
            "high_in",
            "high_out",
            "total_stars",
            "total_perfects",
            "singles_points",
            "doubles_points"
        ]
        widgets = {
            'match': forms.HiddenInput(),
            'team': forms.HiddenInput(),
            "darts_thrown1": forms.widgets.NumberInput(
                attrs={"class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"}
            ),
            "score_left1": forms.widgets.NumberInput(
                attrs={"class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"}
            ),
            "darts_thrown2": forms.widgets.NumberInput(
                attrs={"class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"}
            ),
            "score_left2": forms.widgets.NumberInput(
                attrs={"class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"}
            ),
            "high_in": forms.widgets.NumberInput(
                attrs={"class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"}
            ),
            "high_out": forms.widgets.NumberInput(
                attrs={"class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"}
            ),
            "total_stars": forms.widgets.NumberInput(
                attrs={"class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"}
            ),
            "total_perfects": forms.widgets.NumberInput(
                attrs={"class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"}
            ),
            "singles_points": forms.widgets.NumberInput(
                attrs={"class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"}
            ),
            "doubles_points": forms.widgets.NumberInput(
                attrs={"class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"}
            ),
            "player": forms.widgets.Select(
                attrs={"class": "w-full h-fit px-3 text-base placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"}
            ),
        }

    def clean(self):
        """
        Clean the form and verify that total_perfects is not greater than total_stars.
        """
        super().clean()
        
        total_stars = self.cleaned_data.get("total_stars")
        total_perfects = self.cleaned_data.get("total_perfects")
        if total_perfects is not None:
            if total_perfects * 3 > total_stars:
                raise forms.ValidationError(
                    "Invalid score. Perfects = 3 Stars. Please add 3 Stars to the total Stars per Perfect."
                )

        if any(self.errors):
            return self.errors
        
        return self.cleaned_data


PlayerScoreFormSet = forms.modelformset_factory(ScoreSummary, form=PlayerScoreSummaryForm, formset=BasePlayerScoreFormSet, extra=4, max_num=4)
TeamScoreFormSet = forms.modelformset_factory(TeamScoreSummary, form=TeamScoreSummaryForm, formset=BaseTeamScoreFormSet, extra=2, max_num=2)
