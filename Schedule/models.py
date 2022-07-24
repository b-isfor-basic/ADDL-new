import datetime
import uuid

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

from django_extensions.db.models import CreationDateTimeField, AutoSlugField

from Locations.models import Division, Establishment
from Members.models import Team


class Season(models.Model):
    seasonNum = models.PositiveIntegerField("Season Number")
    startDate = models.DateField()
    endDate = models.DateField()
    playoffFinalsDate = models.DateTimeField("Playoff Finals")
    playoffFinalsLocation = models.ForeignKey(
        to=Establishment, blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ["-seasonNum"]
        get_latest_by = ["startDate"]

    def __str__(self):
        return f"Season {self.seasonNum}"

    def is_active(self):
        before_today = datetime.date.today() - self.startDate
        after_today = self.playoffFinalsDate - timezone.now()
        return before_today.days > 0 and after_today.days > 0


class Match(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    season = models.ForeignKey(Season, models.CASCADE)
    division = models.ForeignKey(Division, models.CASCADE)
    weekNum = models.IntegerField(blank=True, null=True)
    matchDate = models.DateField(blank=True, null=True)
    boards = ArrayField(
        models.PositiveIntegerField(blank=True, null=True),
        size=2,
        null=True,
        blank=True
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
        if self.teamscore_set.all() != None:
            homeTeamScore = self.teamscore_set.get(team=self.homeTeam)
            awayTeamScore = self.teamscore_set.get(team=self.awayTeam)
            if homeTeamScore.match_points == awayTeamScore.match_points:
                result = "Tie"
            elif homeTeamScore.match_points > awayTeamScore.match_points:
                result = self.homeTeam
            else:
                result = self.awayTeam
            return result
        else:
            return None


class Announcement(models.Model):
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