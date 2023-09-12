from django.db import models
from django.db.models import F, Value
from django.db.models.functions import Concat, Coalesce


def _get_latest_season():
    from Schedule.models import Season

    if Season.objects.exists():
        return Season.objects.latest().season_number
    return None


class DivisionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_num_active_teams(self, season=None):
        if season is None:
            season = _get_latest_season()

        qs = self.get_queryset()
        return qs.annotate(
            num_teams=models.Count(
                "team__id", filter=models.Q(team__season__season_number=season)
            )
        )

    def with_names(self):
        qs = self.get_queryset()

        return qs.annotate(
            area_nm=Coalesce(F("area__shortName"), F("area__name")),
            name=Concat(
                F("area_nm"),
                Value(" - "),
                F("matchNight"),
                output_field=models.CharField(),
            ),
        )

    def get_average_rating(self, season=None):
        from Scores.models import ScoreSummary

        if season is None:
            season = _get_latest_season()

        qs = self.get_queryset().filter(season__season_number=season)
        ratings = ScoreSummary.stats.filter(team__season__season_number=season).filter(
            team__division=models.OuterRef("id"),
            player__in=models.OuterRef("team__players__id"),
        ).values("team__division", "team").rating()

        return qs.annotate(
            area_avg_rating=models.Avg(models.Subquery(ratings.values("rating_score"))),
            num_teams=models.Count(
                "team",
                filter=models.Q(team__season__season_number=season),
                distinct=True,
            ),
        )
