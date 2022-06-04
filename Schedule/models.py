import datetime
import uuid

from django.db import models
from django.utils import timezone
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
    division = models.ForeignKey(Division, models.CASCADE)
    weekNum = models.IntegerField(blank=True, null=True)
    matchDate = models.DateField(blank=True, null=True)
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

    def winner(self):
        if self.teamscore_set.all() != None:
            homeTeamScore = self.teamscore_set.filter('team'==self.homeTeam).matchPoints
            awayTeamScore = self.teamscore_set.filter('team'==self.awayTeam).matchPoints
            if homeTeamScore == awayTeamScore:
                result = 'Tie'
            elif homeTeamScore > awayTeamScore:
                result = self.homeTeam
            else:
                result = self.awayTeam
        return result
