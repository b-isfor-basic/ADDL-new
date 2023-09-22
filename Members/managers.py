from typing import Any

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
from django.db.models.functions import Concat, JSONObject, Least
from django.db.models.lookups import GreaterThanOrEqual, LessThan, LessThanOrEqual


class PlayerStatsManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("team__set", "playerscoresummary_set")
        )


class TeamStatsManager(models.Manager):
    """
    This is a custom manager that adds the following fields to the Team model:
        total_darts_thrown: The total number of darts thrown by the team in all games.
        total_score_left: The total number of points left on the board by the team in all games.
        games_included: The total number of games played by the team.
        best_501_game: The fewest number of darts thrown by the team in a 501 game.
        avg_ppd: The average number of points per dart thrown by the team in all games.

    get_points(): The total number of points scored by the team in all games. Can be filtered.
    """

    def get_queryset(self, *args, **kwargs):
        return (
            super()
            .get_queryset()
            .prefetch_related("players", "teamscoresummary_set", "scoresummary_set")
        )

    def names(self):
        return (
            self.get_queryset()
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

    def best_ppd(self, q=None, *args, **kwargs):
        # Return the best week's points per dart for the team.
        from Scores.models import TeamScoreSummary

        q=kwargs.get('season', None)

        qs = self.get_queryset()
        team_stats = TeamScoreSummary.team_stats.filter(match__week__season=q)

        return qs.annotate(
            best_week_ppd=Max(
                team_stats.filter(team=OuterRef("id")).values("best_week_doubles_ppd"),
            )
        )

    def rating(self, q=None, *args, **kwargs):
        # Return the average rating score of the team's players.
        from Scores.models import ScoreSummary

        q = kwargs.get('season', None)

        qs = self.get_queryset()
        ratings = ScoreSummary.stats.filter(match__week__season=q).filter(
            team=OuterRef("id"), player__in=OuterRef("players__id")
        )

        return qs.annotate(
            team_rating_score=Avg(models.Subquery(ratings.values("rating_score"))),
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
        qs = self.get_queryset()

        q = kwargs.get('season', None)

        return qs.annotate(
            total_points=(
                Sum("scoresummary__singles_points", default=0, filter=Q(scoresummary__match__week__season=q))
                + Sum("scoresummary__doubles_points", default=0, filter=Q(scoresummary__match__week__season=q))
            ),
        )

    def stats(self, q=None, *args, **kwargs):
        season = kwargs.get('season', None)

        qs = self.get_queryset()
        names_qs = self.names()
        pts_qs = self.total_points(season=season).values("id", "total_points")
        best_ppd_qs = self.best_ppd(season=season).values("id", "best_week_ppd")
        rating_qs = self.rating(season=season).values("id", "team_rating_score", "team_rating")

        return qs.annotate(
            team_name=Subquery(names_qs.filter(id=OuterRef("id")).values("team_name")),
            total_darts_thrown=(
                Sum("teamscoresummary__darts_thrown1", filter=Q(teamscoresummary__darts_thrown1__isnull=False, teamscoresummary__match__week__season=season))
                + Sum("teamscoresummary__darts_thrown2", filter=Q(teamscoresummary__darts_thrown2__isnull=False, teamscoresummary__match__week__season=season))
            ),
            total_score_left=(
                Sum("teamscoresummary__score_left1", filter=Q(teamscoresummary__darts_thrown1__isnull=False, teamscoresummary__match__week__season=season))
                + Sum("teamscoresummary__score_left2",filter=Q(teamscoresummary__darts_thrown2__isnull=False, teamscoresummary__match__week__season=season))
            ),
            games_included=(Count("teamscoresummary__id", distinct=True, filter=Q(teamscoresummary__match__week__season=season)) * 2),
            best_501_game=Least(
                Min(
                    "teamscoresummary__darts_thrown1",
                    filter=Q(teamscoresummary__score_left1=0,  teamscoresummary__match__week__season=season)
                ),
                Min(
                    "teamscoresummary__darts_thrown2",
                    filter=Q(teamscoresummary__score_left2=0,  teamscoresummary__match__week__season=season)
                ),
                Value(1000),
            ),
            avg_ppd=(
                ((501.0 * F("games_included")) - F("total_score_left"))
                / F("total_darts_thrown")
            ),
            best_week_ppd=Subquery(
                best_ppd_qs.filter(id=OuterRef("id")).distinct().values("best_week_ppd")
            ),
            team_rating_score=Subquery(
                rating_qs.filter(id=OuterRef("id")).distinct().values("team_rating_score")
            ),
            team_rating=Subquery(
                rating_qs.filter(id=OuterRef("id")).distinct().values("team_rating")
            ),
            total_points=Subquery(
                pts_qs.filter(id=OuterRef("id")).distinct().values("total_points")
            ),
        ).filter(total_darts_thrown__isnull=False)

    # TODO: This is not returning the correct total points value. It isn't filtering by season.
    def weekly_points(self, *args, **kwargs):
        from Schedule.models import Season
        from Scores.models import ScoreSummary

        season = kwargs.get('season', None)

        # Return the total number of points scored by the team in all games. Can be filtered.
        qs = self.get_queryset()
        names_qs = self.names()
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

        return qs.annotate(
            team_name=Subquery(names_qs.filter(id=OuterRef("id")).values("team_name")),
            total_points=Subquery(
                pts_qs.filter(id=OuterRef("id")).values("total_points")
            ),
        ).annotate(
            scores=ArraySubquery(scores),
        )


class TeamDetailsManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
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
