from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from django_extensions.db.models import TimeStampedModel
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField

from .managers import RegistrationManager, TeamDetailsManager, TeamStatsManager


class Player(AbstractUser):
    """
    All users are current, past, or potential players in the league. Created
    to add required phone number field to default User model.

    Phone number is necessary to communicate with the opposing team regarding
    rescheduling matches and for the area manager to facilitate league
    operation.
    """

    phoneNumber = PhoneNumberField("Phone Number", blank=True)

    class Meta:
        verbose_name = "player"
        verbose_name_plural = "players"
        ordering = ["first_name", "last_name", "username"]

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
        players: The players that make up the team.
        division: The division the team is assigned to.
        season: The season the team is registered for.
    """

    players = models.ManyToManyField(
        "Player", related_name="teams", max_length=2, db_index=True
    )
    season = models.ManyToManyField("Schedule.Season", through="Registration")
    division = ChainedManyToManyField(chained_field="season", chained_model_field="divisions", to="Locations.Division", through="Registration")

    objects = models.Manager()
    details = TeamDetailsManager()
    stats = TeamStatsManager()

    def get_matches(self, season='Season.objects.latest()', *args, **kwargs):
        """
        Returns the matches for the team for the given season.
        """
        if "season" in kwargs:
            season = kwargs.get("season")

        matches = self.awayMatches.filter(week__season=season)
        return matches.union(
            self.homeMatches.filter(week__season=season)
        ).order_by("week__week_number")

    def name(self):
        plyrs = self.players.all()
        return plyrs[0].last_name + "/" + plyrs[1].last_name

    def __str__(self):
        return self.name()


class Registration(TimeStampedModel, models.Model):
    """
    A registration holds a team's membership for a season. A team can have
    multiple registrations, but only one per season.
    """

    class Meta:
        verbose_name = "Team Registration"
        verbose_name_plural = "Team Registrations"
        ordering = ["-season", "division", "team"]
        unique_together = ["season", "team"]

    team = models.ForeignKey(to="Team", related_name="registrations", on_delete=models.CASCADE)
    season = models.ForeignKey("Schedule.Season", models.CASCADE, db_index=True)
    division = ChainedForeignKey(
        "Locations.division",
        chained_field="season",
        chained_model_field="season",
        auto_choose=True,
        sort=True,
    )

    objects = models.Manager()
    details = RegistrationManager()

    def __str__(self):
        return f"{self.team} (S{self.season.season_number})"
