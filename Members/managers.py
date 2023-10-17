from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.expressions import ArraySubquery
from django.db import models
from django.db.models import (
    Avg,
    Case,
    Count,
    F,
    Max,
    Min,
    OuterRef,
    Q,
    Subquery,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Concat, JSONObject, Least, Greatest, Coalesce
from django.db.models.lookups import GreaterThanOrEqual, LessThan, LessThanOrEqual


class PlayerStatsManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("team__set", "scoresummary_set")
        )


class TeamStatsQuerySet(models.QuerySet):
    def names(self):
        return self.annotate(
            players_names=ArrayAgg("players__last_name"),
            team_name=Concat(
                F("players_names__0"),
                Value("/"),
                F("players_names__1"),
                output_field=models.CharField(),
            ),
        ).values("id", "team_name")

    def best_ppd(self, *args, **kwargs):
        # Return the best week's points per dart for the team.
        from Schedule.models import Season
        from Scores.models import TeamScoreSummary

        season = (
            kwargs.get("season") if "season" in kwargs else Season.objects.latest().id
        )
        team_stats = (
            TeamScoreSummary.stats.filter(match__week__season=season)
            .best_week_doubles_ppd()
            .values("team", "best_week_doubles_ppd")
        )

        return self.annotate(
            best_week_ppd=Max(
                team_stats.filter(team=OuterRef("id")).values("best_week_doubles_ppd"),
            )
        )

    def rating(self, *args, **kwargs):
        # Return the average rating score of the team's players.
        from Scores.models import ScoreSummary
        from Schedule.models import Season

        season = (
            kwargs.get("season") if "season" in kwargs else Season.objects.latest().id
        )
        ratings = (
            ScoreSummary.stats.filter(match__week__season=season)
            .rating()
            .values("team", "player")
            .annotate(rating_score=F("rating_score"))
        )

        return self.annotate(
            team_rating_score=Avg(
                ratings.filter(team=OuterRef("id"))
                .filter(player__in=OuterRef("players"))
                .values("rating_score")
            ),
            team_rating=Case(
                When(LessThanOrEqual(F("team_rating_score"), 10.50), then=Value("E")),
                When(LessThan(F("team_rating_score"), 12.20), then=Value("D")),
                When(LessThan(F("team_rating_score"), 15.40), then=Value("C")),
                When(LessThan(F("team_rating_score"), 18.80), then=Value("B")),
                When(LessThan(F("team_rating_score"), 22.50), then=Value("A")),
                When(
                    GreaterThanOrEqual(F("team_rating_score"), 22.50), then=Value("AA")
                ),
            ),
        )

    def total_points(self, *args, **kwargs):
        # Return the total number of points scored by the team in all games. Can be filtered.
        from Schedule.models import Season

        season = (
            kwargs.get("season") if "season" in kwargs else Season.objects.latest().id
        )

        return self.annotate(
            total_points=(
                Sum(
                    "scoresummary__singles_points",
                    default=0,
                    filter=Q(scoresummary__match__week__season=season),
                )
                + Sum(
                    "scoresummary__doubles_points",
                    default=0,
                    filter=Q(scoresummary__match__week__season=season),
                )
            ),
        )

    def weekly_points(self, *args, **kwargs):
        from Schedule.models import Season
        from Scores.models import ScoreSummary

        season = (
            kwargs.get("season") if "season" in kwargs else Season.objects.latest().id
        )

        # Return the total number of points scored by the team in all games. Can be filtered.
        pts_qs = self.total_points(season=season).values("id", "total_points")

        scores = (
            ScoreSummary.objects.filter(team=OuterRef("id"), match__week__season=season)
            .values(week=F("match__week__week_number"))
            .annotate(
                weekly_pts=Sum("singles_points", filter=Q(match__week__season=season))
                + Sum("doubles_points", filter=Q(match__week__season=season))
            )
            .values(json=JSONObject(week=F("week"), points=F("weekly_pts")))
        )

        return (
            self.names()
            .annotate(
                total_points=Subquery(
                    pts_qs.filter(id=OuterRef("id")).values("total_points")
                ),
                team_div=F("division__id"),
            )
            .annotate(
                scores=ArraySubquery(scores),
            )
        )

    def stats(self, *args, **kwargs):
        # Return the total number of points scored by the team in all games. Can be filtered.
        from Schedule.models import Season
        from Scores.models import TeamScoreSummary

        season = (
            kwargs.get("season") if "season" in kwargs else Season.objects.latest().id
        )
        pts_qs = self.total_points(season=season).values("id", "total_points")
        best_ppd_qs = self.best_ppd(season=season).values("id", "best_week_ppd")
        rating_qs = self.rating(season=season).values(
            "id", "team_rating_score", "team_rating"
        )
        avg_ppd_qs = (
            TeamScoreSummary.stats.filter(match__week__season=season)
            .avg_doubles_ppd()
            .values("team", "avg_doubles_ppd")
        )

        return self.names().annotate(
            best_501_game=Least(
                Min(
                    "teamscoresummary__darts_thrown1",
                    filter=Q(
                        teamscoresummary__score_left1=0,
                        teamscoresummary__match__week__season=season,
                    ),
                ),
                Min(
                    "teamscoresummary__darts_thrown2",
                    filter=Q(
                        teamscoresummary__score_left2=0,
                        teamscoresummary__match__week__season=season,
                    ),
                ),
                Value(1000),
            ),
            avg_ppd=Greatest(
                Subquery(
                    avg_ppd_qs.filter(team=OuterRef("id"))
                    .distinct()
                    .values("avg_doubles_ppd")
                ),
                Value(0.0),
                output_field=models.DecimalField(decimal_places=4, max_digits=6),
            ),
            best_week_ppd=Greatest(
                Subquery(
                    best_ppd_qs.filter(id=OuterRef("id"))
                    .distinct()
                    .values("best_week_ppd")
                ),
                Value(0.0),
                output_field=models.DecimalField(decimal_places=4, max_digits=6),
            ),
            team_rating_score=Greatest(
                Subquery(
                    rating_qs.filter(id=OuterRef("id"))
                    .distinct()
                    .values("team_rating_score")
                ),
                Value(0.0),
                output_field=models.DecimalField(decimal_places=4, max_digits=6),
            ),
            team_rating=Coalesce(
                Subquery(
                    rating_qs.filter(id=OuterRef("id")).distinct().values("team_rating")
                ),
                Value(""),
            ),
            total_points=Greatest(
                Subquery(
                    pts_qs.filter(id=OuterRef("id")).distinct().values("total_points")
                ),
                Value(0),
            ),
        )


class TeamStatsManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "players",
                "scoresummary_set",
                "teamscoresummary_set",
                "season",
                "division",
            )
        )


class TeamDetailsManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related('players', 'division', 'season')
            .prefetch_related('players__scoresummary_set', 'players__last_name')
            .annotate(
                players_names=ArrayAgg("players__last_name"),
                team_name=Concat(
                    F("players_names__0"),
                    Value("/"),
                    F("players_names__1"),
                    output_field=models.CharField(),
                ),
            )
            .values("id", "team_name")
        )


class RegistrationManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("team__players", "season", "division")
            .annotate(
                players_names=ArrayAgg("team__players__last_name"),
                team_name=Concat(
                    F("players_names__0"),
                    Value("/"),
                    F("players_names__1"),
                    output_field=models.CharField(),
                ),
                seasons_played=Count("season", distinct=True),
                latest_season=Max("season__season_number"),
            )
        )

    def create(self, **kwargs):
        return super().create(**kwargs)
