import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import F
from django.db.models.aggregates import Sum, Min, Max
from django.utils.translation import gettext_lazy as _

from django_extensions.db.models import TimeStampedModel

from Members.models import Team
from Schedule.models import Match

class DoublesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(format='DB')


class SinglesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(format='SN')


class BaseScore(models.Model):
    """
    Base game score model for all games: cricket, 501, and 301. All games
    include scores for stars, perfects, and game point.
    """
    class Meta:
        abstract = True   

    SINGLES = 'SN'
    DOUBLES = 'DB'
    GAME_FORMAT_CHOICES = [
        (SINGLES, 'Singles'),
        (DOUBLES, 'Doubles')
    ]

    id = models.UUIDField(default=uuid.uuid1, primary_key=True, editable=False)
    scoreset = models.ForeignKey(to='Scoreset', on_delete=models.CASCADE)
    stars = models.PositiveIntegerField(blank=True, null=True)
    perfects = models.PositiveIntegerField(blank=True, null=True)
    game_point = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(1, "Game point cannot exceed 1.")],
    )
    format = models.CharField(max_length=2, choices=GAME_FORMAT_CHOICES)

    objects = models.Manager()
    doubles_games = DoublesManager()
    singles_games = SinglesManager()

class Cricket(BaseScore, models.Model):
    """
    Cricket game stats are the same as base score stats. Each player should
    complete 2 singles games and 2 doubles games.
    """
    pass


class Three01(BaseScore, models.Model):
    """
    301 is always doubles format. Adds in and out fields to track
    highs for awards at season's end.
    """
    in_thrown = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MaxValueValidator(170, "In cannot exceed 170.")],
    )
    out_thrown = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MaxValueValidator(170, "Out cannot exceed 170.")],
    )


class Five01(BaseScore, models.Model):
    """
    501 adds darts_thrown and score_left fields for PPD calculation.
    Out_thrown tracks highs for awards at season's end. Players complete
    two singles 501 games and 2 doubles 501 games.
    """
    darts_thrown = models.PositiveIntegerField(blank=True, null=True)
    score_left = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MaxValueValidator(501, "Score left cannot exceed 501.")],
    )
    out_thrown = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MaxValueValidator(170, "Out cannot exceed 170.")],
    )


class Scoreset(TimeStampedModel, models.Model):
    """
    Links player scores to match for game result and stat calculation.
    """
    match = models.ForeignKey(Match, models.CASCADE)
    team = models.ForeignKey(Team, models.CASCADE)
    player = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    is_sub = models.BooleanField()

    def singles_points(self):
        cricket_singles_wins = Cricket.singles_games.filter(scoreset=self.id).aggregate(Sum('game_point', default=0))
        five01_singles_wins = Five01.singles_games.filter(scoreset=self.id).aggregate(Sum('game_point', default=0))
        return cricket_singles_wins['game_point__sum'] + five01_singles_wins['game_point__sum']

    def doubles_points(self):
        cricket_doubles_wins = Cricket.doubles_games.filter(scoreset=self.id).aggregate(Sum('game_point', default=0))
        three01_doubles_wins = Three01.doubles_games.filter(scoreset=self.id).aggregate(Sum('game_point', default=0))
        five01_doubles_wins = Five01.doubles_games.filter(scoreset=self.id).aggregate(Sum('game_point', default=0))
        return cricket_doubles_wins['game_point__sum'] + three01_doubles_wins['game_point__sum'] + five01_doubles_wins['game_point__sum']

    def match_points(self):
        return self.singles_points() + self.doubles_points()

    def singles_ppd(self):
        total_thrown = Five01.singles_games.filter(scoreset=self.id).aggregate(Sum('darts_thrown'))
        total_scored = Five01.singles_games.filter(scoreset=self.id).aggregate(Sum('score_left'))
        return (1002 - total_scored['score_left__sum']) / total_thrown['darts_thrown__sum']

    def best_singles_501(self):
        low_thrown = Five01.singles_games.filter(scoreset=self.id, game_point=1).aggregate(Min('darts_thrown'))
        return low_thrown['darts_thrown__min']

    def best_doubles_501(self):
        low_thrown = Five01.doubles_games.filter(scoreset=self.id, game_point=1).aggregate(Min('darts_thrown'))
        return low_thrown['darts_thrown__min']

    def high_in(self):
        high_in = Three01.doubles_games.filter(scoreset=self.id).aggregate(Max('in_thrown', default=0))
        return high_in['in_thrown__max']

    def high_out(self):
        high_out_301 = Three01.doubles_games.filter(scoreset=self.id).aggregate(Max('out_thrown', default=0))
        high_out_501 = Five01.objects.filter(scoreset=self.id).aggregate(Max('out_thrown', default=0))
        return max(high_out_301['out_thrown__max'], high_out_501['out_thrown__max'])

# class PlayerStats(models.Model):


# class TeamStats(models.Model):
#     team = models.ForeignKey(Team, models.DO_NOTHING)
#     matchPoints = models.PositiveIntegerField(
#         validators=[MaxValueValidator(
#             20,
#             f'Total match points for {team} cannot be greater than 20. Please review and try again.'
#         )]
#     )


# class PlayerScore(models.Model):
#     match = models.ForeignKey(Match, models.PROTECT)
#     player = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT)
#     is_sub = models.BooleanField(
#         "Subs",
#         "Sub",
#     )
#     team = models.ForeignKey(Team, models.PROTECT)
#     stars = models.PositiveIntegerField(blank=True, null=True)
#     perfects = models.PositiveIntegerField(blank=True, null=True)
#     singles_points = models.PositiveIntegerField(blank=True, null=True)
#     doubles_points = models.PositiveIntegerField(blank=True, null=True)
#     match_points = models.PositiveIntegerField(null=True)
#     high_in = models.PositiveIntegerField(blank=True, null=True)
#     high_out = models.PositiveIntegerField(blank=True, null=True)
#     best_501 = models.PositiveIntegerField(blank=True, null=True)
#     darts_thrown = models.PositiveIntegerField()
#     score_left = models.PositiveIntegerField(blank=True, null=True)
#     created_at = CreationDateTimeField()
#     modified_at = ModificationDateTimeField()
# 
#     @property
#     def weeklyPPD(self):
#         return (1002 - self.score_left) / self.darts_thrown
# 
# 
# class TeamScore(models.Model):
#     team = models.ForeignKey(Team, models.PROTECT)
#     match = models.ForeignKey(Match, models.PROTECT)
#     match_points = models.PositiveIntegerField(null=True)
#     best_501 = models.PositiveIntegerField(blank=True, null=True)
#     darts_thrown = models.PositiveIntegerField()
#     score_left = models.PositiveIntegerField(blank=True, null=True)
# 
#     @property
#     def weeklyPPD(self):
#         return (1002 - self.score_left) / self.darts_thrown
# 