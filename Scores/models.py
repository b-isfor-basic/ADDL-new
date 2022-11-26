import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from django.db.models.signals import post_save
from django.dispatch import receiver

from .managers import *

from Members.models import Team
from Schedule.models import Match


class GameScore(models.Model):
    """
    A single game score for a player in a match.

    Fields:
        id: A unique identifier for the score.
        scoreset: The scoreset for the player.
        match: The match the score is for.
        format: The format of the game (SN = singles, DB = doubles).
        game: The game type (CKT = cricket, 501 = 501, 301 = 301).
        stars: The number of stars the player earned.
        perfects: The number of perfects the player earned.
        game_point: Points earned is 1 if player wins.
        out_thrown: In 501 or 301, the score the winning player hit to finish the game.
            Only one player per team can have a non-zero value.
        in_thrown: In 301, the score a player hit to start the game.
            Only one player per team can have a non-zero value.
        darts_thrown: The number of darts thrown by the player/team.
        score_left: The score left on the board when the game ended.
            If score left is 0, the player/team won the game.
    """

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
        blank=True,
        null=True,
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
    games = GamesManager()
    query = GameQuerySet.as_manager()

    @property
    def player_display(self):
        return (
            "("
            + str(self.scoreset.match.weekNum)
            + ") "
            + self.scoreset.player.last_name
        )


class Scoreset(TimeStampedModel, models.Model):
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
        unique_together = ["match", "player"]

    @property
    def player_display(self):
        return "(" + str(self.match.weekNum) + ") " + self.player.last_name


class Approval(TimeStampedModel, models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    approved_by = models.ForeignKey("Members.Player", on_delete=models.DO_NOTHING)
    approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ["match", "approved_by"]

    @receiver(post_save, sender=Scoreset)
    def create_approval(sender, instance, created, **kwargs):
        if created:
            Approval.objects.create(match=instance.match)
