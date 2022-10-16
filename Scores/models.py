import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models.aggregates import Count, Max, Min, Sum
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from Members.models import Team
from Schedule.models import Match


class GameQuerySet(models.QuerySet):
    def doubles(self, **kwargs):
        return super(GameQuerySet, self).filter(format='DB', **kwargs)
    
    def singles(self, **kwargs):
        return super(GameQuerySet, self).filter(format='SN', **kwargs)

    def five01_singles(self, **kwargs):
        return super(GameQuerySet, self).filter(format='SN', game='501', **kwargs)
    
    def five01_doubles(self, **kwargs):
        return super(GameQuerySet, self).filter(format='DB', game='501', **kwargs)

    def wins(self, **kwargs):
        return super(GameQuerySet, self).filter(game_point=1, **kwargs)


class SinglesCricketGameManager(models.Manager):
    def create(self, **kwargs):
        format = 'SN'
        game = 'CKT'
        return super().create(format=format, game=game, **kwargs)


class DoublesCricketGameManager(models.Manager):
    def create(self, **kwargs):
        format = 'DB'
        game = 'CKT'
        return super().create(format=format, game=game, **kwargs)


class Singles501GameManager(models.Manager):
    def create(self, **kwargs):
        format = 'SN'
        game = '501'
        return super().create(format=format, game=game, **kwargs)


class Doubles501GameManager(models.Manager):
    def create(self, **kwargs):
        format = 'DB'
        game = '501'
        return super().create(format=format, game=game, **kwargs)


class Doubles301GameManager(models.Manager):
    def create(self, **kwargs):
        format = 'DB'
        game = '301'
        return super().create(format=format, game=game, **kwargs)



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
    singles_cricket = SinglesCricketGameManager()
    doubles_cricket = DoublesCricketGameManager()
    singles_501 = Singles501GameManager()
    doubles_501 = Doubles501GameManager()
    doubles_301 = Doubles301GameManager()

    @property
    def player_display(self):
        return '(' + str(self.scoreset.match.weekNum) + ') ' + self.scoreset.player.last_name


class ScoresetManager(models.Manager):
    
    def get_queryset(self):
        return super(ScoresetManager,self).get_queryset().annotate(
            Sum('gamescore__game_point')
        )

    def create_new(self, match, team, player):
        if player.team_set.first() == team:
            sub = False
        else: 
            sub = True
        scoreset = self.create(
            match=match,
            team=team,
            player=player,
            is_sub=sub
        )
        return scoreset



class Scoreset(models.Model):
    """
    Links all of a player's games to the corresponding match for game result and stat calculation.
    """

    match = models.ForeignKey(Match, models.CASCADE)
    team = models.ForeignKey(Team, models.CASCADE)
    player = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    is_sub = models.BooleanField()

    objects = models.Manager()
    details = ScoresetManager()

    class Meta:
        unique_together = ['match', 'player']

    @property
    def player_display(self):
        return '(' + str(self.match.weekNum) + ') ' + self.player.last_name

    @property
    def singles_points(self):
        points = GameScore.games.singles(scoreset=self.id).aggregate(
            Sum("game_point", default=0)
        )
        return points["game_point__sum"]

    @property
    def doubles_points(self):
        points = GameScore.games.doubles(scoreset=self.id).aggregate(
            Sum("game_point", default=0)
        )
        return points["game_point__sum"]

    @property
    def match_points(self):
        return self.singles_points() + self.doubles_points()

    @property
    def singles_ppd(self):
        total_thrown = GameScore.games.five01_singles(scoreset=self.id).aggregate(
            Sum("darts_thrown"), Count("id")
        )
        total_scored = (501 * total_thrown["id__count"]) - (GameScore.games.five01_singles(scoreset=self.id).aggregate(
            Sum("score_left", default=0)
        ))
        return total_scored["score_left__sum"] / total_thrown["darts_thrown__sum"]

    @property
    def best_singles_501(self):
        low_thrown = GameScore.games.five01_singles(
            scoreset=self.id, 
            game_point=1
        ).aggregate(
            Min("darts_thrown")
        )
        return low_thrown["darts_thrown__min"]

    @property
    def best_doubles_501(self):
        low_thrown = GameScore.games.five01_doubles(
            scoreset=self.id, game_point=1
        ).aggregate(Min("darts_thrown"))
        return low_thrown["darts_thrown__min"]

    @property
    def high_in(self):
        high_in = GameScore.objects.filter(scoreset=self.id).aggregate(
            Max("in_thrown", default=0)
        )
        return high_in["in_thrown__max"]

    @property
    def high_out(self):
        high_out = GameScore.objects.filter(scoreset=self.id).aggregate(
            Max("out_thrown", default=0)
        )
        return high_out["out_thrown__max"]

