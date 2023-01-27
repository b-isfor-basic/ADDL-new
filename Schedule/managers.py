from django.db.models import Manager, Q, Sum, Count, Avg
from django.utils import timezone

class MatchManager(Manager):
    def by_season(self, season):
        return self.get_queryset().filter(season__season_number=season)

    def by_division(self, division):
        return self.get_queryset().filter(division=division)

    def by_player(self, player):
        return self.get_queryset().filter(Q(awayTeam=player.team) | Q(homeTeam=player.team))



class SeasonManager(Manager):
    def get_active(self):
        season_start_before_today = Q(match_play_start_dt__lte=timezone.now())
        season_end_after_today = Q(match_play_end_dt__gte=timezone.now())

        if (
            self.get_queryset()
            .filter(season_start_before_today & season_end_after_today)
            .exists()
        ):
            return (
                self.get_queryset()
                .filter(season_start_before_today & season_end_after_today)
                .first()
            )
       
        return self.get_queryset().latest("match_play_start_dt")

