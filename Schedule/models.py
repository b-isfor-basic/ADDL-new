import datetime
import uuid

from django.db import models
from django.db.models import Sum, Q, Count, F
from django.utils import timezone
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

from django_extensions.db.models import CreationDateTimeField, AutoSlugField

from Locations.models import Division, Establishment
from Members.models import Team


class Season(models.Model):
    """
    Season match play lasts for 9 to 11 weeks based on the number of 
    teams registered in each area and can accommodate 4, 5, 6, 8, 9, 
    10, 11, or 12 teams in each division. 

    There is 1 week at the end of the season for make-up matches and
    1 week for in-house seeded playoff preliminary matches. The final
    league-wide playoff tournament is on the second Saturday following the
    in-house playoffs.
    """

    seasonNum = models.PositiveIntegerField("Season Number")
    startDate = models.DateField()
    endDate = models.DateField()
    # TODO: Move playoff info to a new model with 1 to 1 relationship.
    playoffFinalsDate = models.DateTimeField("Playoff Finals")
    playoffFinalsLocation = models.ForeignKey(
        to=Establishment, blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ["-seasonNum"]
        get_latest_by = ["startDate"]

    def __str__(self):
        return f"Season {self.seasonNum}"

    def active(self):
        before_today = datetime.date.today() - self.startDate
        after_today = self.playoffFinalsDate - timezone.now()
        return before_today.days > 0 and after_today.days > 0


class Match(models.Model):
    """
    
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

    class Meta:
        verbose_name_plural = "Matches"

    def __str__(self):
        return f"{self.awayTeam} vs. {self.homeTeam}"

    @property
    def winner(self):
        home_scores = self.scoreset_set.filter(team=self.homeTeam)
        homeTeamScore = home_scores.first().match_points() + home_scores.last().match_points()
        away_scores = self.scoreset_set.filter(team=self.homeTeam)
        awayTeamScore = away_scores.first().match_points() + away_scores.last().match_points()
        total_score = self.scoreset_set.filter(cricket__game_point__gt=0).count()
        if total_score > 0:
            if homeTeamScore == awayTeamScore:
                result = "Tie"
            elif homeTeamScore > awayTeamScore:
                result = self.homeTeam
            else:
                result = self.awayTeam
            return result
        else:
            return None


class Announcement(models.Model):
    """
    Holds front page announcements such as season creation dates, 
    team registration deadlines, etc. Requires an active date and
    expiration date to remove messages that are no longer relevant.
    """

    title = models.CharField(max_length=100)
    title_slug = AutoSlugField(populate_from="title")
    body = models.TextField()
    active_date = models.DateTimeField()
    inactive_date = models.DateTimeField()
    season = models.ForeignKey(Season, models.CASCADE, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    date_created = CreationDateTimeField()

    def __str__(self):
        return str(self.title).title()
