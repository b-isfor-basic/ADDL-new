import uuid

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from Schedule.models import Match
from Members.models import Team


    
class PlayerScore(models.Model):
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


class TeamScore(models.Model):
    team = models.ForeignKey(Team, models.DO_NOTHING)
    matchPoints = models.PositiveIntegerField(
        validators=[MaxValueValidator(
            20, 
            f'Total match points for {team} cannot be greater than 20. Please review and try again.'
        )]
    )
