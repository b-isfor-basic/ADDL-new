import uuid

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.db.models.signals import pre_save
from django.dispatch import receiver

from Members.models import Team
from Schedule.models import Match

from .managers import (PlayerScoreSummaryManager,
                       TeamScoreSummaryManager)


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


class TeamScoreSummary(TimeStampedModel, models.Model):
    """
    Holds the summary of a team's scores for a match. Used for calculating
    team stats.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, db_index=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, db_index=True)
    darts_thrown1 = models.IntegerField(blank=True, null=True)
    score_left1 = models.IntegerField(blank=True, null=True)
    darts_thrown2 = models.IntegerField(blank=True, null=True)
    score_left2 = models.IntegerField(blank=True, null=True)

    objects = models.Manager()
    team_stats = TeamScoreSummaryManager()

    @property
    def weekly_ppd(self):
        if self.darts_thrown1 is None:
            self.darts_thrown1 = 50
        if self.darts_thrown2 is None:
            self.darts_thrown2 = 50
        if self.score_left1 is None:
            self.darts_thrown1 = 50
            self.score_left1 = 2
        if self.score_left2 is None:
            self.darts_thrown2 = 50
            self.score_left2 = 2
        darts_thrown = self.darts_thrown1 + self.darts_thrown2
        scored = 1001 - (self.score_left1 + self.score_left2)
        return round(scored / darts_thrown, 4)

    class Meta:
        unique_together = ["match", "team"]
        verbose_name = "Team Score Summary"
        verbose_name_plural = "Team Score Summaries"


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
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
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
    stats = PlayerScoreSummaryManager()

    class Meta:
        unique_together = ["match", "player"]
        verbose_name = "Player Score Summary"
        verbose_name_plural = "Player Score Summaries"

    @property
    def total_points(self):
        return self.singles_points + self.doubles_points

    @property
    def singles_weekly_ppd(self):
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
    score_summary = models.OneToOneField(ScoreSummary, on_delete=models.CASCADE, blank=True, null=True)
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


# Old score management models. Kept for reference.
# 
# class GameScore(models.Model):
#     """
#     A single game score for a player in a match.

#     Fields:
#         id: A unique identifier for the score.
#         scoreset: The scoreset for the player.
#         match: The match the score is for.
#         format: The format of the game (SN = singles, DB = doubles).
#         game: The game type (CKT = cricket, 501 = 501, 301 = 301).
#         stars: The number of stars the player earned.
#         perfects: The number of perfects the player earned.
#         game_point: Points earned is 1 if player wins.
#         out_thrown: In 501 or 301, the score the winning player hit to finish
#         the game.
#             Only one player per team can have a non-zero value.
#         in_thrown: In 301, the score a player hit to start the game.
#             Only one player per team can have a non-zero value.
#         darts_thrown: The number of darts thrown by the player/team.
#         score_left: The score left on the board when the game ended.
#             If score left is 0, the player/team won the game.
#     """

#     SINGLES = "SN"
#     DOUBLES = "DB"
#     FORMAT_CHOICES = [(SINGLES, "Singles"), (DOUBLES, "Doubles")]

#     CRICKET = "CKT"
#     FIVE01 = "501"
#     THREE01 = "301"
#     GAME_CHOICES = [
#         (CRICKET, "Cricket"),
#         (FIVE01, "501"),
#         (THREE01, "301"),
#     ]

#     id = models.UUIDField(default=uuid.uuid1, primary_key=True, editable=False)
#     scoreset = models.ForeignKey(to="Scoreset", on_delete=models.CASCADE)
#     format = models.CharField(max_length=2, choices=FORMAT_CHOICES)
#     game = models.CharField(max_length=3, choices=GAME_CHOICES)
#     stars = models.PositiveIntegerField(blank=True, null=True)
#     perfects = models.PositiveIntegerField(blank=True, null=True)
#     game_point = models.PositiveIntegerField(
#         blank=True,
#         null=True,
#         validators=[MaxValueValidator(1, "Game point cannot exceed 1.")],
#     )
#     # 301 only stat
#     in_thrown = models.PositiveIntegerField(
#         blank=True,
#         null=True,
#         validators=[MaxValueValidator(170, "In cannot exceed 170.")],
#     )
#     # 501 & 301 stat
#     out_thrown = models.PositiveIntegerField(
#         blank=True,
#         null=True,
#         validators=[MaxValueValidator(170, "Out cannot exceed 170.")],
#     )
#     # 501 only stats
#     darts_thrown = models.PositiveIntegerField(blank=True, null=True)
#     score_left = models.PositiveIntegerField(
#         blank=True,
#         null=True,
#         validators=[MaxValueValidator(501, "Score left cannot exceed 501.")],
#     )

#     objects = models.Manager()
#     games = GamesManager()
#     query = GameQuerySet.as_manager()

#     @property
#     def player_display(self):
#         return (
#             "("
#             + str(self.scoreset.match.week.week_number)
#             + ") "
#             + self.scoreset.player.last_name
#         )


# class Scoreset(TimeStampedModel, models.Model):
#     """
#     Links all of a player's games to the corresponding match for game result
#     and stat calculation.
#     """

#     match = models.ForeignKey(Match, models.CASCADE)
#     team = models.ForeignKey(Team, models.CASCADE)
#     player = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
#     is_sub = models.BooleanField()

#     objects = models.Manager()
#     details = ScoresetManager()

#     class Meta:
#         unique_together = ["match", "player"]

#     @property
#     def player_display(self):
#         return "(" + str(self.match.week.week_number) + ") " + self.player.last_name

#     @property
#     def singles_weekly_ppd(self):
#         return self.gamescore.filter(
#             gamescore__format="SN",
#         )


# class Approval(TimeStampedModel, models.Model):
#     match = models.ForeignKey(Match, on_delete=models.CASCADE)
#     approved_by = models.ForeignKey("Members.Player", on_delete=models.DO_NOTHING)
#     approved = models.BooleanField(default=False)

#     class Meta:
#         unique_together = ["match", "approved_by"]

#     @receiver(post_save, sender=Scoreset)
#     def create_approval(sender, instance, created, **kwargs):
#         if created:
#             Approval.objects.create(match=instance.match)