import uuid

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models
from django.core.exceptions import ValidationError

from django_extensions.db.models import CreationDateTimeField, ModificationDateTimeField
from Schedule.models import Match
from Members.models import Team


class BaseScore(models.Model):
    FORMAT_CHOICES = [
        ('SNGL', 'Singles'),
        ('DBLS', 'Doubles')
    ]

    score_id = models.UUIDField(
        default=uuid.uuid1, 
        primary_key=True, 
        editable=False
    )
    scoreset = models.ForeignKey('Scoreset', models.CASCADE)
    format = models.CharField(max_length=4, choices=FORMAT_CHOICES)
    stars = models.PositiveIntegerField(blank=True, null=True)
    perfects = models.PositiveIntegerField(blank=True, null=True)
    game_point = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(1, "Game point cannot exceed 1.")],
    )


class Three01(BaseScore):
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


class Five01(BaseScore):
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


class Scoreset(models.Model):
    match = models.ForeignKey(Match, models.CASCADE)
    team = models.ForeignKey(Team, models.CASCADE)
    player = models.ForeignKey(User, models.CASCADE)
    is_sub = models.BooleanField()
    created_at = CreationDateTimeField()
    modified_at = ModificationDateTimeField()

    @property
    def singles_wins(self):
        return Scoreset.get(id=self.id).basescore_set.count(format='SNGL', game_point=1)

    @property
    def doubles_wins(self):
        return Scoreset.get(id=self.id).basescore_set.count(format='DBLS', game_point=1)
    
    @property
    def total_points(self):
        return Scoreset.get(id=self.id).basescore_set.count(game_point=1)

        
# class PlayerStats(models.Model):



# class TeamStats(models.Model):
#     team = models.ForeignKey(Team, models.DO_NOTHING)
#     matchPoints = models.PositiveIntegerField(
#         validators=[MaxValueValidator(
#             20, 
#             f'Total match points for {team} cannot be greater than 20. Please review and try again.'
#         )]
#     )
