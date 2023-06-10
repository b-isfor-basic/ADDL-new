from django.db import models
from django.db.models import F, Value
from django.db.models.functions import Concat


class DivisionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def num_active_teams(self, season=None):
        if season is None:
            from Schedule.models import Season

            season = Season.details.latest().season_number

        qs = self.get_queryset()
        return qs.annotate()

    def matches(self, season=None):
        qs = self.get_queryset()
        return (
            qs.values(week_number="scheduleweek__week_number")
            .annotate(
                num_matches=models.Count("scheduleweek__match_set"),
            )
            .order_by("week_number")
        )

    def with_names(self):
        qs = self.get_queryset()

        return qs.annotate(
            area_nm=F("area__shortName"),
            name=Concat(
                F("area_nm"),
                Value(" - "),
                F("matchNight"),
                output_field=models.CharField(),
            ),
        )

    def get_average_rating(self, season=None):
        from Schedule.models import Season
        from Scores.models import ScoreSummary

        if season is None:
            season = Season.details.latest().season_number

        qs = self.get_queryset().filter(season__season_number=season)
        ratings = ScoreSummary.stats.filter(team__season__season_number=season).filter(
            team__division=models.OuterRef("id"),
            player__in=models.OuterRef("team__players__id"),
        )

        return qs.annotate(
            area_avg_rating=models.Avg(models.Subquery(ratings.values("rating_score")))
        )
