import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import F, Sum
from recurrence.fields import RecurrenceField

from Locations.models import Division, Establishment
from Members.models import Player, Team

from .managers import MatchManager, ScheduleManager, SeasonManager


class ScheduleRule(models.Model):
    class Meta:
        verbose_name_plural = "Schedule Rules"
        verbose_name = "Schedule Rule"

    title = models.CharField(max_length=48)
    description = models.TextField(null=True, blank=True)
    frequency = RecurrenceField()


class Season(models.Model):
    """
    Season match play lasts for 9 to 11 weeks based on the number of
    teams registered in each area and can accommodate 4, 5, 6, 8, 9,
    10, 11, or 12 teams in each division.

    There is 1 week at the end of the season for make-up matches and
    1 week for in-house seeded playoff preliminary matches. The final
    league-wide playoff tournament is traditionally held on the second
    Saturday following the in-house playoffs.
    """

    class Meta:
        ordering = ["-season_number"]
        get_latest_by = ["match_play_start_dt"]

    season_number = models.PositiveIntegerField("Season Number", db_index=True)
    match_play_start_dt = models.DateField(db_index=True)
    match_play_end_dt = models.DateField(db_index=True)
    playoff_finals_dt = models.DateTimeField("Playoff Finals")
    playoffFinalsLocation = models.ForeignKey(
        to=Establishment, blank=True, null=True, on_delete=models.SET_NULL
    )
    divisions = models.ManyToManyField(Division, db_index=True)

    objects = models.Manager()
    details = SeasonManager()

    def __str__(self):
        return f"Season {self.season_number}"

    @property
    def num_weeks_regular_season(self):
        """
        Returns the number of weeks in the season.
        """
        num_weeks = (self.match_play_end_dt - self.match_play_start_dt).days // 7
        return list(range(1, num_weeks, 1))


class ScheduleWeek(models.Model):
    """
    ScheduleWeeks are used to track the progress of the season.
    """

    season = models.ForeignKey(Season, models.CASCADE, db_index=True)
    week_number = models.PositiveIntegerField(db_index=True)
    match_date = models.DateField()
    division = models.ForeignKey(Division, models.CASCADE, db_index=True)
    playoff_week = models.BooleanField(default=False)

    objects = models.Manager()
    details = ScheduleManager()

    class Meta:
        unique_together = ["season", "week_number", "division"]

    def __str__(self):
        return f"S{self.season.season_number} - W{self.week_number} - Area {self.division.area.number}"


class Match(models.Model):
    """
    Scheduled matches.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    week = models.ForeignKey(ScheduleWeek, models.CASCADE, null=True, db_index=True)
    boards = ArrayField(
        models.PositiveIntegerField(blank=True, null=True),
        size=2,
        null=True,
        blank=True,
    )
    awayTeam = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="awayMatches",
        db_index=True,
    )
    homeTeam = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="homeMatches",
        db_index=True,
    )

    objects = models.Manager()
    details = MatchManager()

    class Meta:
        verbose_name_plural = "Matches"

    def __str__(self):
        return f"{self.awayTeam} vs. {self.homeTeam}"

    @property
    def homeScore(self):
        homeScore = self.scoresummary_set.filter(team=self.homeTeam).aggregate(
            home_pts=Sum(F("singles_points") + F("doubles_points"), default=0)
        )
        return homeScore["home_pts"]

    @property
    def awayScore(self):
        awayScore = self.scoresummary_set.filter(team=self.awayTeam).aggregate(
            away_pts=Sum(F("singles_points") + F("doubles_points"), default=0)
        )
        return awayScore["away_pts"]


class Announcement(models.Model):
    """
    Holds front page announcements such as season creation dates,
    team registration deadlines, etc. Requires an active date and
    expiration date to remove messages that are no longer relevant.
    """

    title = models.CharField(max_length=100)
    body = models.TextField()
    active_date = models.DateTimeField()
    inactive_date = models.DateTimeField()
    created_by = models.ForeignKey(
        Player, models.SET_NULL, null=True, related_name="announcements_created"
    )
    edited_by = models.ForeignKey(
        Player,
        models.SET_NULL,
        null=True,
        blank=True,
        related_name="announcements_edited",
    )

    def __str__(self):
        return str(self.title).title()
