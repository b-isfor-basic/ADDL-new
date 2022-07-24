from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.db.models import Sum, Max, Min

from phonenumber_field.modelfields import PhoneNumberField



class Player(AbstractUser):
    '''
    All users are current, past, or potential players in the league. Created 
    to add required phone number field to default User model.
    '''
    phoneNumber = PhoneNumberField()

    class Meta:
        verbose_name = 'player'
        verbose_name_plural = 'players'


class Team(models.Model):
    player1 = models.ForeignKey(
        'Player',
        models.CASCADE,
        related_name= 'team_member_1'
    )
    player2 = models.ForeignKey(
        'Player',
        models.CASCADE,
        related_name= 'team_member_2'
    )
    division = models.ForeignKey('Locations.Division', models.CASCADE)
    season = models.ForeignKey('Schedule.Season', models.CASCADE)

    def __str__(self):
        return f'{self.player1.last_name}/{self.player2.last_name}'


class PlayerSeasonInstance(models.Model):
    '''
    Model contains a player's stat records for a single season. Also holds
    player's teammate for the season. 
    '''
    player = models.ForeignKey(Player, models.CASCADE)
    season = models.ForeignKey(
        'Schedule.Season', 
        models.CASCADE
    )
    division = models.ForeignKey(
        'Locations.Division', 
        models.SET_NULL,
        null=True
    )
    partner = models.OneToOneField(
        'self',
        models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.player.last_name

    def matches_played(self):
        return self.playerscore_set.count()

    def total_stars(self):
        return self.playerscore_set.aggregate(Sum('stars'))

    def average_stars_per_game(self):
        return self.total_stars() / (self.matches_played() * 10)

    def total_perfects(self):
        return self.playerscore_set.aggregate(Sum('perfects'))


