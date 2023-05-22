from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

from Members.models import Player
from Scores.models import Forfeit, ScoreSummary, TeamScoreSummary

CLASS_ATTRS = "w-full h-fit px-3 text-sm placeholder-slate-400 text-slate-200  bg-slate-800 border border-slate-900/30 rounded-full shadow-inner shadow-slate-900/30 focus:outline-none focus:ring-1 focus:ring-amber-400 focus:ring-opacity-100 focus:border-transparent"

class BaseTeamScoreFormSet(forms.BaseModelFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        match = kwargs.pop("match")
        if index < 1:
            if match.teamscoresummary_set.exists():
                pk = match.teamscoresummary_set.filter(team=match.awayTeam)[0].id
            else:
                pk = None
            kwargs.update(
                {
                    "prefix": "away-team",
                    "initial": {"pk": pk, "match": match.id, "team": match.awayTeam},
                }
            )
        else:
            if match.teamscoresummary_set.exists():
                pk = match.teamscoresummary_set.filter(team=match.homeTeam)[0].id
            else:
                pk = None
            kwargs.update(
                {
                    "prefix": "home-team",
                    "initial": {"pk": pk, "match": match.id, "team": match.homeTeam},
                }
            )
        return kwargs

    def clean(self):
        """
        Verify that only one team has 0 score left for each game.
        """
        cleaned_data = super().clean()

        pts_left = []
        for form in self.forms:
            score_left1 = form.cleaned_data.get("score_left1")
            score_left2 = form.cleaned_data.get("score_left2")
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

        return cleaned_data
    

class TeamScoreSummaryForm(forms.ModelForm):
    """
    Summarized match scores for entry by area managers.
    """

    mark_as_forfeit = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.widgets.CheckboxInput(
            attrs={
                "class": "checkbox rounded-md h-[18px] w-[18px] bg-slate-800 border shadow-slate-900/30 shadow-inner focus:ring-0 focus:outline-none"
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
            "darts_thrown1": forms.widgets.NumberInput(attrs={"class": CLASS_ATTRS}),
            "score_left1": forms.widgets.NumberInput(attrs={"class": CLASS_ATTRS}),
            "darts_thrown2": forms.widgets.NumberInput(attrs={"class": CLASS_ATTRS}),
            "score_left2": forms.widgets.NumberInput(attrs={"class": CLASS_ATTRS}),
        }

    def clean(self):
        """
        Verify if the match is being marked as a forfeit.
        """
        cleaned_data = super().clean()

        forfeit = cleaned_data.get("mark_as_forfeit")
        if forfeit:
            record = Forfeit.objects.create(
                match=cleaned_data.get("match"),
                team=cleaned_data.get("team"),
            )
            record.save()
            return record

        if any(self.errors):
            return

        return cleaned_data


class BasePlayerScoreFormSet(forms.BaseModelFormSet):
    def get_queryset(self):
        return super().get_queryset().select_related("player", "team", "match").order_by("match__awayTeam", "match__homeTeam")

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        match = kwargs.pop("match")
        if index < 2:
            if match.scoresummary_set.exists():
                qs = match.scoresummary_set.filter(team=match.awayTeam)
                player = qs[index].player.id
                pk = qs[index].id
            else:
                player = match.awayTeam.players.all()[index].id
                pk = None
            kwargs.update(
                {
                    "prefix": f"away-player-{index}",
                    "initial": {"pk": pk, "match": match.id, "team": match.awayTeam, "player": player},
                }
            )
        else:
            player_num = index - 2
            if match.scoresummary_set.exists():
                qs = match.scoresummary_set.filter(team=match.homeTeam)
                player = qs[player_num].player.id
                pk = qs[player_num].id
            else:
                player = match.homeTeam.players.all()[player_num].id
                pk = None
            kwargs.update(
                {
                    "prefix": f"home-player-{player_num}",
                    "initial": {"pk": pk, "match": match.id, "team": match.homeTeam, "player": player},
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
            singles = form.cleaned_data.get("singles_points")
            doubles = form.cleaned_data.get("doubles_points")
            if singles is None:
                singles = 0
            if doubles is None:
                doubles = 0
            total_points += singles 
            total_points += doubles
            doubles_pts.append(doubles)

        if total_points != 20:
            raise forms.ValidationError(
                "Invalid score. Total points for match must equal 20."
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

        return cleaned_data


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
            "doubles_points",
        ]

        widgets = {
            "match": forms.HiddenInput(),
            "team": forms.HiddenInput(),
            "darts_thrown1": forms.widgets.NumberInput(attrs={"class": CLASS_ATTRS}),
            "score_left1": forms.widgets.NumberInput(attrs={"class": CLASS_ATTRS}),
            "darts_thrown2": forms.widgets.NumberInput(attrs={"class": CLASS_ATTRS}),
            "score_left2": forms.widgets.NumberInput(attrs={"class": CLASS_ATTRS}),
            "high_in": forms.widgets.NumberInput(attrs={"class": CLASS_ATTRS}),
            "high_out": forms.widgets.NumberInput(attrs={"class": CLASS_ATTRS}),
            "total_stars": forms.widgets.NumberInput(attrs={"class": CLASS_ATTRS}),
            "total_perfects": forms.widgets.NumberInput(attrs={"class": CLASS_ATTRS}),
            "singles_points": forms.widgets.NumberInput(attrs={"class": CLASS_ATTRS}),
            "doubles_points": forms.widgets.NumberInput(attrs={"class": CLASS_ATTRS}),
            "player": forms.widgets.Select(
                attrs={
                    "class": CLASS_ATTRS,
                    ":disabled": "isOpen()",
                    ":class": " isOpen() ? 'cursor-not-allowed' : '' ",
                    "x-ref": "select",
                    ":value": " selectedPlayer() ",
                },
                choices=Player.objects.all().values_list("id", "first_name", "last_name").order_by("first_name", "last_name"),
            ),
        }

    # Fields to add a new player to the database
    first_name = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={
                "class": CLASS_ATTRS,
                "x-ref": "firstName",
            }
        )
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={
                "class": CLASS_ATTRS,
                "x-ref": "lastName",
            }
        )
    )

    def total_points_check(self, singles_points=0, doubles_points=0):
        ''' Checks that the total points for the player does not exceed 10.'''

        if singles_points | doubles_points:
            if singles_points + doubles_points > 10:
                raise forms.ValidationError(
                    "Invalid score. Total points for player cannot exceed 10 points."
                )

    def perfects_check(self, total_perfects=0, total_stars=0):
        '''Checks that there are at least 3 stars per perfect'''

        if total_perfects is not None:
            if total_perfects * 3 > total_stars:
                raise forms.ValidationError(
                    "Invalid score. Perfects = 3 Stars. Please add 3 Stars to the total Stars per Perfect."
                )

    def clean(self):
        """
        Clean the form and verify that total_perfects is not greater than total_stars.
        """
        cleaned_data = super().clean()

        total_stars = cleaned_data.get("total_stars")
        total_perfects = cleaned_data.get("total_perfects")

        singles_points = cleaned_data.get("singles_points")
        doubles_points = cleaned_data.get("doubles_points")

        self.total_points_check(singles_points, doubles_points)
        self.perfects_check(total_perfects, total_stars)

        if self.errors:
            return

        return cleaned_data


# Old score entry forms. Kept for reference.
# 
#  class ScoresetForm(forms.ModelForm):
#     class Meta:
#         model = Scoreset
#         fields = ["player"]
#         widgets = {"player": forms.widgets.Input()}


# class GameScoreForm(forms.ModelForm):
#     class Meta:
#         model = GameScore
#         fields = [
#             "stars",
#             "perfects",
#             "game_point",
#             "in_thrown",
#             "out_thrown",
#             "darts_thrown",
#             "score_left",
#         ]
#         widgets = {
#             "stars": forms.widgets.NumberInput(
#                 attrs={"class": "ss-left", "placeholder": "stars"}
#             ),
#             "perfects": forms.widgets.NumberInput(
#                 attrs={"class": "ss-center", "placeholder": "perfects"}
#             ),
#             "in_thrown": forms.widgets.NumberInput(
#                 attrs={"class": "ss-center", "placeholder": "in"}
#             ),
#             "out_thrown": forms.widgets.NumberInput(
#                 attrs={"class": "ss-center", "placeholder": "out"}
#             ),
#             "darts_thrown": forms.widgets.NumberInput(
#                 attrs={"class": "ss-center", "placeholder": "thrown"}
#             ),
#             "score_left": forms.widgets.NumberInput(
#                 attrs={"class": "ss-right", "placeholder": "left"}
#             ),
#             "game_point": forms.widgets.NumberInput(),
#         }