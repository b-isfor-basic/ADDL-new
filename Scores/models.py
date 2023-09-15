import uuid

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator
from django.db import models
from django_extensions.db.models import TimeStampedModel
from smart_selects.db_fields import ChainedForeignKey

from Members.models import Team
from Schedule.models import Match

from .managers import (
    ForfeitManager,
    PlayerScoreSummaryManager,
    PlayerScoreSummaryQuerySet,
    TeamScoreSummaryManager,
    TeamScoreSummaryQuerySet,
)


class Forfeit(TimeStampedModel, models.Model):
    """
    A forfeit for a match.

    Fields:
        id: A unique identifier for the forfeit.
        match: The match the forfeit is for.
        team: The team that forfeited.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, db_index=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, db_index=True)

    objects = models.Manager()
    details = ForfeitManager()

    class Meta:
        unique_together = ["match", "team"]
        verbose_name = "Forfeit"
        verbose_name_plural = "Forfeits"

    objects = models.Manager()
    details = ForfeitManager()

    class Meta:
        unique_together = ["match", "team"]
        verbose_name = "Forfeit"
        verbose_name_plural = "Forfeits"


class TeamScoreSummary(TimeStampedModel, models.Model):
    """
    Holds the summary of a team's scores for a match. Used for calculating
    team stats.
    """

    class Meta:
        unique_together = ["match", "team"]
        verbose_name = "Team Score Summary"
        verbose_name_plural = "Team Score Summaries"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, db_index=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, db_index=True)
    darts_thrown1 = models.IntegerField(
        blank=True, null=True, validators=[MaxValueValidator(50)]
    )
    score_left1 = models.IntegerField(blank=True, null=True)
    darts_thrown2 = models.IntegerField(
        blank=True, null=True, validators=[MaxValueValidator(50)]
    )
    score_left2 = models.IntegerField(blank=True, null=True)

    objects = models.Manager()
    stats = TeamScoreSummaryManager.from_queryset(TeamScoreSummaryQuerySet)()

    @property
    def get_weekly_ppd(self):
        if self.darts_thrown1 is None and self.darts_thrown2 is None:
            return None
        elif self.darts_thrown1 is None:
            self.darts_thrown1 = 50
        elif self.darts_thrown2 is None:
            self.darts_thrown2 = 50
        elif self.score_left1 is None:
            self.darts_thrown1 = 50
            self.score_left1 = 2
        elif self.score_left2 is None:
            self.darts_thrown2 = 50
            self.score_left2 = 2
        darts_thrown = self.darts_thrown1 + self.darts_thrown2
        scored = 1001 - (self.score_left1 + self.score_left2)
        return round(scored / darts_thrown, 4)


class ScoreSummary(TimeStampedModel, models.Model):
    """
    Holds summarized scores for each Player in a Match. Creation of this model
    is limited to area managers and admins.
    Objects may also be created by the create_summary method in the ScoreDetail
    model.
    """

    class Meta:
        unique_together = ["match", "player"]
        verbose_name = "Score Summary"
        verbose_name_plural = "Score Summaries"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, db_index=True)
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True
    )
    is_sub = models.BooleanField(default=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, db_index=True)
    total_stars = models.IntegerField(blank=True, null=True)
    total_perfects = models.IntegerField(blank=True, null=True)
    singles_points = models.IntegerField(default=0)
    doubles_points = models.IntegerField(default=0)
    high_in = models.IntegerField(blank=True, null=True)
    high_out = models.IntegerField(blank=True, null=True)
    darts_thrown1 = models.IntegerField(blank=True, null=True)
    score_left1 = models.IntegerField(blank=True, null=True)
    darts_thrown2 = models.IntegerField(blank=True, null=True)
    score_left2 = models.IntegerField(blank=True, null=True)

    objects = models.Manager()
    stats = PlayerScoreSummaryManager.from_queryset(PlayerScoreSummaryQuerySet)()
    stats = PlayerScoreSummaryManager.from_queryset(PlayerScoreSummaryQuerySet)()

    @property
    def total_points(self):
        return self.singles_points + self.doubles_points

    @property
    def weekly_ppd(self):
        if self.darts_thrown1 is None and self.darts_thrown2 is None:
            return None
        elif self.darts_thrown1 is None:
            self.darts_thrown1 = 50
        elif self.darts_thrown2 is None:
            self.darts_thrown2 = 50
        elif self.score_left1 is None:
            self.darts_thrown1 = 50
            self.score_left1 = 2
        elif self.score_left2 is None:
            self.darts_thrown2 = 50
            self.score_left2 = 2
        elif self.darts_thrown1 is None:
            self.darts_thrown1 = 50
        elif self.darts_thrown2 is None:
            self.darts_thrown2 = 50
        elif self.score_left1 is None:
            self.darts_thrown1 = 50
            self.score_left1 = 2
        elif self.score_left2 is None:
            self.darts_thrown2 = 50
            self.score_left2 = 2
        darts_thrown = self.darts_thrown1 + self.darts_thrown2
        scored = 1001 - (self.score_left1 + self.score_left2)
        return round(scored / darts_thrown, 4)


class ScoreDetail(TimeStampedModel, models.Model):
    """
    A detailed breakdown of a player's scores for a match. Only created when
    scores are submitted by a player and not by an area manager or admin.
    """

    class Meta:
        unique_together = ["match", "player"]
        verbose_name = "Score Detail"
        verbose_name_plural = "Score Details"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    score_summary = models.OneToOneField(
        ScoreSummary, on_delete=models.CASCADE, blank=True, null=True
    )
    stars_list = ArrayField(
        models.PositiveIntegerField(), max_length=10, blank=True, null=True
    )
    perfects_list = ArrayField(
        models.PositiveIntegerField(), max_length=10, blank=True, null=True
    )
    points_list = ArrayField(
        models.PositiveIntegerField(MaxValueValidator(1)),
        max_length=10,
        blank=True,
        null=True,
    )
    darts_thrown_list = ArrayField(
        models.PositiveIntegerField(MaxValueValidator(50)),
        max_length=2,
        blank=True,
        null=True,
    )
    score_left_list = ArrayField(
        models.PositiveIntegerField(MaxValueValidator(501)),
        max_length=2,
        blank=True,
        null=True,
    )
    in_list = ArrayField(
        models.PositiveIntegerField(MaxValueValidator(170)),
        max_length=2,
        blank=True,
        null=True,
    )
    out_list = ArrayField(
        models.PositiveIntegerField(MaxValueValidator(170)),
        max_length=4,
        blank=True,
        null=True,
    )
