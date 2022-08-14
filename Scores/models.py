import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models.aggregates import Sum, Min, Max
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _

from django_extensions.db.models import TimeStampedModel

from Members.models import Team
from Schedule.models import Match


class GameQuerySet(models.QuerySet):
    def doubles(self):
        return self.filter(format='DB')
    
    def singles(self):
        return self.filter(format='SN')

    def five01_singles(self):
        return self.filter(
            format='SN',
            game='501'
        )
    
    def five01_doubles(self):
        return self.filter(
            format='DB',
            game='501'
        )


class GameScore(models.Model):
    SINGLES = "SN"
    DOUBLES = "DB"
    FORMAT_CHOICES = [(SINGLES, "Singles"), (DOUBLES, "Doubles")]

    CRICKET = "CKT"
    FIVE01 = "501"
    THREE01 = "301"
    GAME_CHOICES = [
        (CRICKET, "Cricket"),
        (FIVE01, "501"),
        (THREE01, "301"),
    ]

    id = models.UUIDField(default=uuid.uuid1, primary_key=True, editable=False)
    scoreset = models.ForeignKey(to="Scoreset", on_delete=models.CASCADE)
    format = models.CharField(max_length=2, choices=FORMAT_CHOICES)
    game = models.CharField(max_length=3, choices=GAME_CHOICES)
    stars = models.PositiveIntegerField(blank=True, null=True)
    perfects = models.PositiveIntegerField(blank=True, null=True)
    game_point = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(1, "Game point cannot exceed 1.")],
    )
    # 301 only stat
    in_thrown = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MaxValueValidator(170, "In cannot exceed 170.")],
    )
    # 501 & 301 stat
    out_thrown = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MaxValueValidator(170, "Out cannot exceed 170.")],
    )
    # 501 only stats
    darts_thrown = models.PositiveIntegerField(blank=True, null=True)
    score_left = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MaxValueValidator(501, "Score left cannot exceed 501.")],
    )

    objects = models.Manager()
    games = GameQuerySet.as_manager()


class ScoresetManager(models.Manager):
    def with_points(self):
        return self.annotate(
            match_points=models.Sum('gamescore__game_point')
        )


class Scoreset(models.Model):
    """
    Links all of a players games to the corresponding match for game result and stat calculation.
    """

    match = models.ForeignKey(Match, models.CASCADE)
    team = models.ForeignKey(Team, models.CASCADE)
    player = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    is_sub = models.BooleanField()

    objects = models.Manager()
    wins = ScoresetManager()

    def singles_points(self):
        points = GameScore.singles_games.filter(scoreset=self.id).aggregate(
            Sum("game_point", default=0)
        )
        return points["game_point__sum"]

    def doubles_points(self):
        points = GameScore.doubles_games.filter(scoreset=self.id).aggregate(
            Sum("game_point", default=0)
        )
        return points["game_point__sum"]

    def match_points(self):
        return self.singles_points() + self.doubles_points()

    def singles_ppd(self):
        total_thrown = GameScore.singles_games.filter(scoreset=self.id).aggregate(
            Sum("darts_thrown")
        )
        total_scored = GameScore.singles_games.filter(scoreset=self.id).aggregate(
            Sum("score_left")
        )
        return (1002 - total_scored["score_left__sum"]) / total_thrown[
            "darts_thrown__sum"
        ]

    def best_singles_501(self):
        low_thrown = GameScore.singles_games.filter(
            scoreset=self.id, game_point=1
        ).aggregate(Min("darts_thrown"))
        return low_thrown["darts_thrown__min"]

    def best_doubles_501(self):
        low_thrown = GameScore.doubles_games.filter(
            scoreset=self.id, game_point=1
        ).aggregate(Min("darts_thrown"))
        return low_thrown["darts_thrown__min"]

    def high_in(self):
        high_in = GameScore.doubles_games.filter(scoreset=self.id).aggregate(
            Max("in_thrown", default=0)
        )
        return high_in["in_thrown__max"]

    def high_out(self):
        high_out = GameScore.objects.filter(scoreset=self.id).aggregate(
            Max("out_thrown", default=0)
        )
        return high_out["out_thrown__max"]
