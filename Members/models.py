from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Player(AbstractUser):
    """
    All users are current, past, or potential players in the league. Created
    to add required phone number field to default User model.

    Phone number is necessary to communicate with the opposing team regarding
    rescheduling matches and for the area manager to facilitate league
    operation.
    """

    phoneNumber = PhoneNumberField('Phone Number', blank=True)

    class Meta:
        verbose_name = "player"
        verbose_name_plural = "players"

    def __str__(self):
        return str(self.get_full_name())


class Team(models.Model):
    """
    A team is a pair of players that play together in a match.
    Teams are created by the area manager and assigned to players.
    Teams can be changed by the area manager at any time, but ideally
    only at the beginning of a season. A team is assigned to one division
    per season. The division cannot be changed during the season.

    Fields:
        player1: The first player on the team.
        player2: The second player on the team.
        division: The division the team is assigned to.
        season: The season the team is registered for.
    """

    player1 = models.ForeignKey("Player", models.CASCADE, related_name="team_member_1")
    player2 = models.ForeignKey("Player", models.CASCADE, related_name="team_member_2")
    division = models.ForeignKey("Locations.Division", models.CASCADE)
    season = models.ForeignKey("Schedule.Season", models.CASCADE)

    def __str__(self):
        return f"{self.player1.last_name}/{self.player2.last_name}"

    class Meta:
        unique_together = (["player1", "season"], ["player2", "season"])
