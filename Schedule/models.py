import uuid

from django.db import models
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField

from recurrence.fields import RecurrenceField

from Locations.models import Division, Establishment
from Members.models import Team, Player

from .managers import SeasonManager, MatchManager


class Scheduler(models.Model):
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

    season_number = models.PositiveIntegerField("Season Number")
    match_play_start_dt = models.DateField()
    match_play_end_dt = models.DateField()
    playoff_finals_dt = models.DateTimeField("Playoff Finals")
    playoffFinalsLocation = models.ForeignKey(
        to=Establishment, blank=True, null=True, on_delete=models.SET_NULL
    )
    divisions = models.ManyToManyField(Division)

    objects = models.Manager()
    details = SeasonManager()

    class Meta:
        ordering = ["-season_number"]
        get_latest_by = ["match_play_start_dt"]

    def __str__(self):
        return f"Season {self.season_number}"


class Match(models.Model):
    """
    Scheduled matches.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    season = models.ForeignKey(Season, models.CASCADE)
    division = models.ForeignKey(Division, models.CASCADE)
    weekNum = models.IntegerField(blank=True, null=True)
    matchDate = models.DateField(blank=True, null=True)
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
    )
    homeTeam = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="homeMatches",
    )

    objects = models.Manager()
    details = MatchManager()

    class Meta:
        verbose_name_plural = "Matches"

    def __str__(self):
        return f"{self.awayTeam} vs. {self.homeTeam}"

    @property
    def homeScore(self):
        homeScore = self.scoreset_set.filter(team=self.homeTeam).aggregate(
            home_pts=Sum("gamescore__game_point", default=0)
        )
        return homeScore["home_pts"]

    @property
    def awayScore(self):
        awayScore = self.scoreset_set.filter(team=self.awayTeam).aggregate(
            away_pts=Sum("gamescore__game_point", default=0)
        )
        return awayScore["away_pts"]

    @property
    def winner(self):
        if (self.homeScore == 0) and (self.awayScore == 0):
            return None
        else:
            if self.homeScore == self.awayScore:
                return "Draw"
            elif self.homeScore > self.awayScore:
                return "Home"
            else:
                return "Away"


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
    created_by = models.ForeignKey(Player, models.SET_NULL, null=True, related_name="announcements_created")
    edited_by = models.ForeignKey(Player, models.SET_NULL, null=True, blank=True, related_name="announcements_edited")

    def __str__(self):
        return str(self.title).title()
