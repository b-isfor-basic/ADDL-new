import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.core.exceptions import ValidationError

from django_extensions.db.models import CreationDateTimeField, ModificationDateTimeField
from Schedule.models import Match
from Members.models import Team


class BaseScore(models.Model):
    '''
    Base game score model for all games: cricket, 501, and 301. All games
    include scores for stars, perfects, and game point.
    '''
    FORMAT_CHOICES = [
        ('SN', 'Singles'),
        ('DB', 'Doubles')
    ]

    score_id = models.UUIDField(
        default=uuid.uuid1, 
        primary_key=True, 
        editable=False
    )
 #   match = models.ForeignKey(Match, models.RESTRICT)
 #   player = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    format = models.CharField(max_length=2, choices=FORMAT_CHOICES)
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
    player = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    is_sub = models.BooleanField()
    created_at = CreationDateTimeField()
    modified_at = ModificationDateTimeField()


    @property
    def singles_wins(self):
        return Scoreset.objects.filter(
                basescore__match=self.match
            ).filter(
                basescore__player=self.player
            ).filter(
                basescore__format='SN'
            ).filter(
                basescore__game_point=1
            ).count()

    @property
    def doubles_wins(self):
        return Scoreset.objects.filter(
                basescore__match=self.match
            ).filter(
                basescore__player=self.player
            ).filter(
                basescore__format='DB'
            ).filter(
                basescore__game_point=1
            ).count()

    @property
    def total_points(self):
        return Scoreset.objects.filter(
                basescore__match=self.match
            ).filter(
                basescore__player=self.player
            ).filter(
                basescore__game_point=1
            ).count()

    @property
    def best_sngl_501(self):
        pass

        
# class PlayerStats(models.Model):



# class TeamStats(models.Model):
#     team = models.ForeignKey(Team, models.DO_NOTHING)
#     matchPoints = models.PositiveIntegerField(
#         validators=[MaxValueValidator(
#             20, 
#             f'Total match points for {team} cannot be greater than 20. Please review and try again.'
#         )]
#     )

class PlayerScore(models.Model):
    match = models.ForeignKey(Match, models.PROTECT)
    player = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT)
    is_sub = models.BooleanField('Subs', 'Sub',)
    team = models.ForeignKey(Team, models.PROTECT)
    stars = models.PositiveIntegerField(blank=True, null=True)
    perfects = models.PositiveIntegerField(blank=True, null=True)
    singles_points = models.PositiveIntegerField(blank=True, null=True)
    doubles_points = models.PositiveIntegerField(blank=True, null=True)
    match_points = models.PositiveIntegerField(null=True)
    high_in = models.PositiveIntegerField(blank=True, null=True)
    high_out = models.PositiveIntegerField(blank=True, null=True)
    best_501 = models.PositiveIntegerField(blank=True, null=True)
    darts_thrown = models.PositiveIntegerField()
    score_left = models.PositiveIntegerField(blank=True, null=True)
    created_at = CreationDateTimeField()
    modified_at = ModificationDateTimeField()

    @property
    def weeklyPPD(self):
        return (1002 - self.score_left)/self.darts_thrown


class TeamScore(models.Model):
    team = models.ForeignKey(Team, models.PROTECT)
    match = models.ForeignKey(Match, models.PROTECT)
    match_points = models.PositiveIntegerField(null=True)
    best_501 = models.PositiveIntegerField(blank=True, null=True)
    darts_thrown = models.PositiveIntegerField()
    score_left = models.PositiveIntegerField(blank=True, null=True)

    @property
    def weeklyPPD(self):
        return (1002 - self.score_left)/self.darts_thrown