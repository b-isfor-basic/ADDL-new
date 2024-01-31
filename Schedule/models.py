import uuid

from django.db import models
from django.db.models import F, Sum

from smart_selects.db_fields import ChainedForeignKey

from Locations.models import Division, Establishment
from Members.models import Player, Team
from Schedule.managers import MatchManager, ScheduleManager, SeasonManager


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
    match_play_start_dt = models.DateField("Match Play Start Date", db_index=True)
    match_play_end_dt = models.DateField("Match Play End Date", db_index=True)
    playoff_finals_dt = models.DateTimeField("Playoff Finals Date")
    playoffFinalsLocation = models.ForeignKey(
        verbose_name="Playoff Finals Location",
        to=Establishment,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
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

    @property
    def get_schedule_weeks_by_division(self):
        """
        Returns a list of schedule weeks for each division.
        """
        return self.scheduleweek_set.all().order_by(
            "division__area__number", "week_number"
        )


class ScheduleWeek(models.Model):
    """
    ScheduleWeeks are used to track the progress of the season.
    """

    class Meta:
        unique_together = ["season", "division", "match_date", "week_number"]
        ordering = ["-season", "division", "week_number"]

    season = models.ForeignKey(Season, models.CASCADE, db_index=True)
    week_number = models.PositiveIntegerField(db_index=True)
    match_date = models.DateField()
    playoff_week = models.BooleanField(default=False)
    division = ChainedForeignKey(
        Division,
        chained_field="season",
        chained_model_field="season",
        show_all=False,
        auto_choose=True,
        sort=True,
        db_index=True,
    )

    objects = models.Manager()
    details = ScheduleManager()

    def __str__(self):
        return f"S{self.season.season_number}.W{self.week_number} - {self.division}"


class Match(models.Model):
    """
    Matches are the individual contests between two teams. A player will have 10 games
    per match, 4 singles and 6 doubles. Each game is worth 1 point. The team with the
    most points at the end of the match wins. Matches can result in a tie.

    Match status is updated automatically when scores are entered or a forfeit is
    reported.

    Status Codes:
        S - Scheduled
        P - Played
        F - Forfeit
    """

    class Meta:
        verbose_name_plural = "Matches"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    week = models.ForeignKey(ScheduleWeek, models.CASCADE, null=True, db_index=True)
    awayTeam = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        related_name="awayMatches",
        db_index=True,
        null=True,
    )
    homeTeam = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        related_name="homeMatches",
        db_index=True,
        null=True,
    )
    status = models.CharField(
        max_length=1,
        choices=[("S", "Scheduled"), ("P", "Played"), ("F", "Forfeit")],
        default="S",
    )

    objects = models.Manager()
    details = MatchManager()

    def __str__(self):
        return f"{self.awayTeam} v. {self.homeTeam}"

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

    def update_status(self):
        if self.scoresummary_set.exists():
            self.status = "P"
        elif self.forfeit_set.exists():
            self.status = "F"
        else:
            self.status = "S"
        self.save()


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
