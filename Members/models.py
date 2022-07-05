from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

class Player(AbstractUser):
    phoneNumber = PhoneNumberField() 

    class Meta:
        verbose_name = 'player'
        verbose_name_plural = 'players'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def matches_played(self):
        return self.playerscore_set.count()


class Team(models.Model):
    player1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        related_name= 'team_member_1'
    )
    player2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        related_name= 'team_member_2'
    )
    division = models.ForeignKey('Locations.Division', models.CASCADE)
    season = models.ForeignKey('Schedule.Season', models.CASCADE)

    def __str__(self):
        return f'{self.player1.last_name}/{self.player2.last_name}'
