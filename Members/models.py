from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from .managers import TeamStatsManager

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
        ordering = ['first_name', 'last_name']

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

    players = models.ManyToManyField("Player", related_name="teams", max_length=2)
    division = models.ForeignKey("Locations.Division", models.CASCADE)
    season = models.ForeignKey("Schedule.Season", models.CASCADE)

    objects = models.Manager()
    stats = TeamStatsManager()

    def __str__(self):
        names = [player.last_name for player in self.players.all()]
        if len(names) < 2:
            return "Invalid Name"
        return f"{names[0]}/{names[1]}"

    @property
    def name(self):
        names = [player.last_name for player in self.players.all()]
        if len(names) < 2:
            return "Invalid Name"
        return f"{names[0]}/{names[1]}"
    
    def weekly_points(self, *args, **kwargs):
        """
        Returns the points per match for the given season.
        """
        from Schedule.models import Season

        if 'season' in kwargs:
            search = models.Q(match__week__season=kwargs['season'])
        else:
            search = models.Q(match__week__season=Season.details.get_active())

        return (self.scoresummary_set
                .filter(search)
                .values('match')
                .annotate(
                    week=models.F('match__week'),
                    match_points=(
                        models.Sum('singles_points') 
                        + models.Sum('doubles_points')
                    )
                )
            )
    
    def season_points(self, *args, **kwargs):
        """
        Returns the points for the given season.
        """
        from Schedule.models import Season

        if 'season' in kwargs:
            search = models.Q(match__week__season=kwargs['season'])
        else:
            search = models.Q(match__week__season=Season.details.get_active())
            
            
        return sum(self.scoresummary_set
                    .filter(search)
                    .values_list('singles_points', 'doubles_points')
                    .aggregate(
                        sngl=models.Sum('singles_points'), 
                        dbls=models.Sum('doubles_points')
                    ).values()
                )

    def get_matches(self, *args, **kwargs):
        """
        Returns the matches for the team for the given season.
        """
        from Schedule.models import Season

        if 'season' in kwargs:
            search = models.Q(week__season=kwargs['season'])
        else:
            search = models.Q(week__season=Season.details.get_active())
            
        matches = self.awayMatches.filter(search)
        return matches.union(self.homeMatches.filter(search).order_by('week__week_number'))
  