import uuid

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from Schedule.models import Match
from Members.models import Team


class PPD(models.Model):
    match = models.ForeignKey(Match, models.RESTRICT)
    darts_thrown1 = models.PositiveIntegerField(blank=True, null=True)
    points_scored1 = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MaxValueValidator(
            501, "Scored points exceed 501. Please correct values and try again.")],
    )
    darts_thrown2 = models.PositiveIntegerField(blank=True, null=True)
    points_scored2 = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MaxValueValidator(
            501, "Scored points exceed 501. Please correct values and try again.")],
    )

    def get_PPD(self):
        if self.darts_thrown1 and self.darts_thrown2 != None:
            total_thrown = self.darts_thrown1 + self.darts_thrown2
            total_scored = self.points_scored1 + self.points_scored2
            return total_scored / total_thrown

    def __str__(self):
        return self.get_PPD()


class PlayerScore(PPD):
    player = models.ForeignKey(User, models.RESTRICT)
    is_sub = models.BooleanField("Is Sub?")
    doubles_points = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(6)],
    )
    singles_points = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(4)],
    )
    stars = models.PositiveIntegerField(default=0)
    perfects = models.PositiveIntegerField(default=0)
    high_in = models.PositiveIntegerField(blank=True, null=True)
    high_out = models.PositiveIntegerField(blank=True, null=True)

    def total_points(self):
        return self.singles_points + self.doubles_points


class TeamScore(PPD):
    team = models.ForeignKey(Team, models.DO_NOTHING)
    matchPoints = models.PositiveIntegerField(
        validators=[MaxValueValidator(
            20, 
            f'Total match points for {team} cannot be greater than 20. Please review and try again.'
        )]
    )
