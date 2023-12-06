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
from django.db.models.functions import Concat, JSONObject, Least, Greatest
from django.db.models.lookups import GreaterThanOrEqual, LessThan, LessThanOrEqual


class PlayerStatsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("team__set", "scoresummary_set")


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
                default=0.0,
            )
        )

    def rating(self, *args, **kwargs):
        # Return the average rating score of the team's players.
        from Scores.models import ScoreSummary
        from Schedule.models import Season

        season = (
            kwargs.get("season") if "season" in kwargs else Season.objects.latest().id
        )
        ratings = ScoreSummary.stats.filter(match__week__season=season).rating(
            season=season
        )

        return self.annotate(
            team_rating_score=Avg(
                ratings.filter(player__in=OuterRef("players")).values("rating_score"),
                default=0.0,
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

    def avg_doubles_ppd(self, *args, **kwargs):
        from Schedule.models import Season

        season = (
            kwargs.get("season") if "season" in kwargs else Season.objects.latest().id
        )

        return self.annotate(
            avg_doubles_ppd=Greatest(
                (
                    (
                        1001.0
                        * Count(
                            "teamscoresummary__match__id",
                            filter=Q(
                                teamscoresummary__darts_thrown1__gte=1,
                                teamscoresummary__darts_thrown2__gte=1,
                                teamscoresummary__match__week__season=season,
                            ),
                        )
                    )
                    - (
                        Sum(
                            "teamscoresummary__score_left1",
                            filter=Q(
                                teamscoresummary__darts_thrown1__gte=1,
                                teamscoresummary__darts_thrown2__gte=1,
                                teamscoresummary__match__week__season=season,
                            ),
                        )
                        + Sum(
                            "teamscoresummary__score_left2",
                            filter=Q(
                                teamscoresummary__darts_thrown1__gte=1,
                                teamscoresummary__darts_thrown2__gte=1,
                                teamscoresummary__match__week__season=season,
                            ),
                        )
                    )
                )
                / (
                    Sum(
                        "teamscoresummary__darts_thrown1",
                        filter=Q(
                            teamscoresummary__darts_thrown1__gte=1,
                            teamscoresummary__darts_thrown2__gte=1,
                            teamscoresummary__match__week__season=season,
                        ),
                    )
                    + Sum(
                        "teamscoresummary__darts_thrown2",
                        filter=Q(
                            teamscoresummary__darts_thrown1__gte=1,
                            teamscoresummary__darts_thrown2__gte=1,
                            teamscoresummary__match__week__season=season,
                        ),
                    )
                ),
                Value(0.0),
            )
        )

    def weekly_points(self, *args, **kwargs):
        from Schedule.models import Season, Match
        from Scores.models import ScoreSummary

        season = (
            kwargs.get("season") if "season" in kwargs else Season.objects.latest().id
        )

        # Return the total number of points scored by the team in all games. Can be filtered.
        pts_qs = self.total_points(season=season).values("id", "total_points")

        scores = (
            Match.objects.filter(
                Q(awayTeam=OuterRef("id")) | Q(homeTeam=OuterRef("id")),
                week__season=season,
            )
            .values(week_num=F("week__week_number"))
            .annotate(
                weekly_pts=Case(
                    When(forfeit__team=OuterRef("id"), then=Value(-1)),
                    When(
                        scoresummary__team=OuterRef("id"),
                        then=(
                            Sum(
                                "scoresummary__singles_points",
                                filter=Q(
                                    week__season=season,
                                    scoresummary__team=OuterRef("id"),
                                ),
                            )
                            + Sum(
                                "scoresummary__doubles_points",
                                filter=Q(
                                    week__season=season,
                                    scoresummary__team=OuterRef("id"),
                                ),
                            )
                        ),
                    ),
                    default=None,
                )
            )
            .values(json=JSONObject(week=F("week_num"), points=F("weekly_pts")))
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
        from Schedule.models import Season

        season = kwargs.get("season") or Season.objects.latest().id

        pts_qs = self.total_points(season=season).values("id", "total_points")
        best_ppd_qs = self.best_ppd(season=season).values("id", "best_week_ppd")
        rating_qs = self.rating(season=season).values(
            "id", "team_rating_score", "team_rating"
        )
        avg_ppd_qs = self.avg_doubles_ppd(season=season).values("id", "avg_doubles_ppd")

        return (
            self.names()
            .annotate(
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
            )
            .values(
                "id",
                "team_name",
                "division__id",
                "best_501_game",
                total_points=Subquery(
                    pts_qs.filter(id=OuterRef("id")).values("total_points")
                ),
                best_week_ppd=Subquery(
                    best_ppd_qs.filter(id=OuterRef("id")).values("best_week_ppd")
                ),
                team_rating_score=Subquery(
                    rating_qs.filter(id=OuterRef("id")).values("team_rating_score")
                ),
                team_rating=Subquery(
                    rating_qs.filter(id=OuterRef("id")).values("team_rating")
                ),
                avg_ppd=Subquery(
                    avg_ppd_qs.filter(id=OuterRef("id")).values("avg_doubles_ppd")
                ),
            )
        )


class TeamStatsManager(models.Manager.from_queryset(TeamStatsQuerySet)):
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
            .select_related("players", "division", "season")
            .prefetch_related("players__scoresummary_set", "players__last_name")
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
