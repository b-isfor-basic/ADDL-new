from django.db import models
from django.db.models import F, Value
from django.db.models.functions import Concat, Coalesce


def _get_latest_season():

    if 'Season.objects.exists()':
        return 'Season.objects.latest()'
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
                "team__id", filter=models.Q(team__season=season)
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

    def get_average_rating(self, *season):
        from Scores.models import TeamScoreSummary
        try:
            ratings = TeamScoreSummary.stats.filter(match__week__season=season).values('team__division', 'team').team_rating() 
        except AttributeError:
            ratings = TeamScoreSummary.stats.filter(match__week__season=_get_latest_season()).values('team__division', 'team').team_rating()

        return super().get_queryset().annotate(
            area_avg_rating=models.Avg(models.Subquery(ratings.filter(team__division=models.OuterRef('id')).values('rating_score')))
        )
