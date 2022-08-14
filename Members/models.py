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
    """

    phoneNumber = PhoneNumberField()

    class Meta:
        verbose_name = "player"
        verbose_name_plural = "players"


class Team(models.Model):
    player1 = models.ForeignKey("Player", models.CASCADE, related_name="team_member_1")
    player2 = models.ForeignKey("Player", models.CASCADE, related_name="team_member_2")
    division = models.ForeignKey("Locations.Division", models.CASCADE)
    season = models.ForeignKey("Schedule.Season", models.CASCADE)

    def __str__(self):
        return f"{self.player1.last_name}/{self.player2.last_name}"

