from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Max, Min, Sum, F
from django.db.models.signals import post_save,m2m_changed
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField


class Player(AbstractUser):
    """
    All users are current, past, or potential players in the league. Created
    to add required phone number field to default User model.

    Phone number is necessary to communicate with the opposing team regarding
    rescheduling matches and for the area manager to facilitate league 
    operation.
    """

    phoneNumber = PhoneNumberField()

    class Meta:
        verbose_name = "player"
        verbose_name_plural = "players"


class Team(models.Model):
    players = models.ManyToManyField('Player')
    division = models.ForeignKey("Locations.Division", models.CASCADE)
    season = models.ForeignKey("Schedule.Season", models.CASCADE)

