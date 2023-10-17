from django.db import models
from django.db.models import F, Value
from django.db.models.functions import Concat, Coalesce
from django.db.models.query import QuerySet


def _get_latest_season():
    if "Season.objects.exists()":
        return "Season.objects.latest()"
    return None


class DivisionQuerySet(models.QuerySet):
    def get_num_active_teams(self, season=None):
        if season is None:
            season = _get_latest_season()

        return self.annotate(
            num_teams=models.Count("team__id", filter=models.Q(team__season=season))
        )

    def with_names(self):
        return self.annotate(
            area_nm=Coalesce(F("area__shortName"), F("area__name")),
            name=Concat(
                F("area_nm"),
                Value(" - "),
                F("matchNight"),
                output_field=models.CharField(),
            ),
        )

    def get_average_rating(self, *args, **kwargs):
        from Schedule.models import Season
        from Scores.models import Team

        season = (
            kwargs.get("season") if "season" in kwargs else Season.objects.latest().id
        )
        team_rating = (
            Team.stats.filter(scoresummary__match__week__season=season)
            .filter(division=models.OuterRef("id"))
            .rating(season=season)
            .values('division')
            .annotate(team_ratings=F('team_rating_score'))
        )
        return self.annotate(
            area_avg_rating=models.Avg(team_rating.values("team_ratings"), default=0),
        )

    def get_schedule_weeks(self, *args, **kwargs):
        from Schedule.models import Season
        season = kwargs.get("season") if "season" in kwargs else Season.objects.latest().id
        return self.annotate(num_weeks=models.Count('scheduleweek', distinct=True, filter=models.Q(scheduleweek__season=season)))
    

class DivisionManager(models.Manager.from_queryset(DivisionQuerySet)):
    def get_queryset(self):
        return super().get_queryset().select_related('area').with_names()
