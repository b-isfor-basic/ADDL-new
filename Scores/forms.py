from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

from Members.models import Player

from .models import GameScore, Scoreset, ScoreSummary, TeamScoreSummary, Forfeit


class ScoresetForm(forms.ModelForm):
    class Meta:
        model = Scoreset
        fields = ["player"]
        widgets = {"player": forms.widgets.Input()}


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
            kwargs.update(
                {
                    "prefix": f"away-player-{index}",
                    "initial": {"match": match.id, "team": match.awayTeam},
                }
            )
        else:
            player_num = index - 2
            kwargs.update(
                {
                    "prefix": f"home-player-{player_num}",
                    "initial": {"match": match.id, "team": match.homeTeam},
                }
            )
        return kwargs

    def clean(self):
        """
        Verify that the total points does not exceed 20 and that doubles points
        for a team match.
        """
        cleaned_data = super().clean()

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
            kwargs.update(
                {
                    "prefix": "away-team",
                    "initial": {"match": match.id, "team": match.awayTeam},
                }
            )
        else:
            kwargs.update(
                {
                    "prefix": "home-team",
                    "initial": {"match": match.id, "team": match.homeTeam},
                }
            )
        return kwargs

    def clean(self):
        """
        Verify that only one team has 0 score left for each game.
        """
        super().clean()

        pts_left = []
        for form in self.forms:
            cleaned_data = form.clean()
            score_left1 = cleaned_data.get("score_left1")
            score_left2 = cleaned_data.get("score_left2")
            team_pts_left = [score_left1, score_left2]
            pts_left.append(team_pts_left)

        for i in list(range(0, 2)):
            if pts_left[0][i] == pts_left[1][i]:
                raise forms.ValidationError(
                    f"Invalid score for Doubles 501 - Game {str(i+1)}. \
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
            attrs={
                "class": "rounded-md h-[18px] w-[18px] text-rose-500 bg-slate-800 border-rose-500 border accent-rose-500 shadow-slate-900/30 shadow-inner focus:ring-0 focus:outline-none"
            }
        ),
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
                attrs={
                    "class": "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"
                }
            ),
            "score_left1": forms.widgets.NumberInput(
                attrs={
                    "class": "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"
                }
            ),
            "darts_thrown2": forms.widgets.NumberInput(
                attrs={
                    "class": "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"
                }
            ),
            "score_left2": forms.widgets.NumberInput(
                attrs={
                    "class": "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"
                }
            ),
        }

    def clean(self):
        """
        Verify if the match is being marked as a forfeit.
        """
        super().clean()

        forfeit = self.cleaned_data.get("mark_as_forfeit")
        if forfeit:
            record = Forfeit.objects.create(
                match=self.cleaned_data.get("match"),
                team=self.cleaned_data.get("team"),
            )
            record.save()
            return record

        if any(self.errors):
            return

        return self.cleaned_data


class PlayerScoreSummaryForm(forms.ModelForm):
    """
    Summarized match scores for entry by area managers.
    """

    # Fields to add a new player to the database
    first_name = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent",
                "x-ref": "firstName",
            }
        ),
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent",
                "x-ref": "lastName",
            }
        ),
    )

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
            "doubles_points",
        ]

        widgets = {
            "match": forms.HiddenInput(),
            "team": forms.HiddenInput(),
            "darts_thrown1": forms.widgets.NumberInput(
                attrs={
                    "class": "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"
                }
            ),
            "score_left1": forms.widgets.NumberInput(
                attrs={
                    "class": "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"
                }
            ),
            "darts_thrown2": forms.widgets.NumberInput(
                attrs={
                    "class": "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"
                }
            ),
            "score_left2": forms.widgets.NumberInput(
                attrs={
                    "class": "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"
                }
            ),
            "high_in": forms.widgets.NumberInput(
                attrs={
                    "class": "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"
                }
            ),
            "high_out": forms.widgets.NumberInput(
                attrs={
                    "class": "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"
                }
            ),
            "total_stars": forms.widgets.NumberInput(
                attrs={
                    "class": "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"
                }
            ),
            "total_perfects": forms.widgets.NumberInput(
                attrs={
                    "class": "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"
                }
            ),
            "singles_points": forms.widgets.NumberInput(
                attrs={
                    "class": "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"
                }
            ),
            "doubles_points": forms.widgets.NumberInput(
                attrs={
                    "class": "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"
                }
            ),
            "player": forms.widgets.Select(
                attrs={
                    "class": "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200 transition-colors duration-200 ease-in-out bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent",
                    ":disabled": "isOpen()",
                    ":class": " isOpen() ? 'cursor-not-allowed' : '' ",
                    "x-ref": "select",
                    ":value": " selectedPlayer() ",
                },
                choices=Player.objects.all().values_list("id", "first_name", "last_name")
            ),
        }

    def total_points_check(self, singles_points=0, doubles_points=0):
        # Checks that the total points for the player does not exceed 10

        if singles_points | doubles_points:
            if singles_points + doubles_points > 10:
                raise forms.ValidationError(
                    "Invalid score. Total points for player cannot exceed 10 points."
                )

    def perfects_check(self, total_perfects=0, total_stars=0):
        # Checks that there are at least 3 stars per perfect

        if total_perfects is not None:
            if total_perfects * 3 > total_stars:
                raise forms.ValidationError(
                    "Invalid score. Perfects = 3 Stars. Please add 3 Stars to the total Stars per Perfect."
                )

    # def player_check(self, player=None, first_name=None, last_name=None):
    #     # Check if player is selected or if first and last name are entered.

    #     if player is None:
    #         if first_name is None or last_name is None:
    #             raise forms.ValidationError(
    #                 "Please select a player or enter a first and last name."
    #             )
    #         else:
    #             first_name = first_name.replace(" ", "")
    #             last_name = last_name.replace(" ", "")
    #             user = f"{first_name.title}.{last_name.title}"
                
    #             if Player.objects.filter(username=user).exists():
    #                 count = Player.objects.filter(username__icontains=user).count()
    #                 user += str(count + 1)
                
    #             player = Player.objects.create(
    #                 first_name=first_name, last_name=last_name, username=user
    #             )
    #             player.save()
    #             return Player.objects.get(username=user)
    #     else:
    #         return player

    def clean(self):
        """
        Clean the form and verify that total_perfects is not greater than total_stars.
        """
        cleaned_data = super().clean()

        # if cleaned_data.get("player") is None:
        #     first_name = cleaned_data.get("first_name")
        #     last_name = cleaned_data.get("last_name")
        #     player = self.player_check(first_name=first_name, last_name=last_name)
        #     cleaned_data["player"] = player
        #     self.instance.player = player
        #     self.errors.clear()
        #     self.is_valid()
        # else:
        #     player = cleaned_data.get("player")

        total_stars = cleaned_data.get("total_stars")
        total_perfects = cleaned_data.get("total_perfects")

        singles_points = cleaned_data.get("singles_points")
        doubles_points = cleaned_data.get("doubles_points")

        self.total_points_check(singles_points, doubles_points)
        self.perfects_check(total_perfects, total_stars)

        if self.errors:
            return

        return cleaned_data
