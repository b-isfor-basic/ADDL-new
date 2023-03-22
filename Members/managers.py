from django.db import models
from django.db.models import Avg, Case, Count, F, Max, Min, OuterRef, Q, Sum, When, Value
from django.db.models.functions import Least
from django.db.models.lookups import GreaterThanOrEqual, LessThan, LessThanOrEqual


class PlayerStatsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("playerscoresummary_set")


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
        qs = super().get_queryset().prefetch_related("teamscoresummary_set")
        return qs.filter(*args, **kwargs).annotate(
            total_darts_thrown=(
                Sum("teamscoresummary__darts_thrown1", distinct=True)
                + Sum("teamscoresummary__darts_thrown2", distinct=True)
            ),
            total_score_left=(
                Sum("teamscoresummary__score_left1", distinct=True)
                + Sum("teamscoresummary__score_left2", distinct=True)
            ),
            games_included=(Count("teamscoresummary__id", distinct=True) * 2.0),
            best_501_game=Least(
                Min(
                    "teamscoresummary__darts_thrown1",
                    filter=Q(teamscoresummary__score_left1=0),
                ),
                Min(
                    "teamscoresummary__darts_thrown2",
                    filter=Q(teamscoresummary__score_left2=0),
                ),
                default=1000,
            ),
            avg_ppd=(
                ((501.0 * F("games_included")) - F("total_score_left"))
                / F("total_darts_thrown")
            ),
        ).filter(total_darts_thrown__isnull=False)

    def rating(self, *args, **kwargs):
        # Return the average rating score of the team's players.
        from Scores.models import ScoreSummary

        qs = super().get_queryset().prefetch_related("scoresummary_set", "players")
        ratings = ScoreSummary.stats.filter(*args, **kwargs).filter(
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
                When(GreaterThanOrEqual(F("team_rating_score"), 22.50), then=Value("AA")),
            ),
        ).filter(team_rating_score__isnull=False)

    def get_points(self, *args, **kwargs):
        # Return the total number of points scored by the team in all games. Can be filtered.
        qs = super().get_queryset().prefetch_related("scoresummary_set", "players")
        return qs.filter(*args, **kwargs).annotate(
            total_points=Sum("scoresummary__singles_points")
            + Sum("scoresummary__doubles_points")
        ).filter(total_points__isnull=False)
    
    def stats(self, *args, **kwargs):
        from Scores.models import TeamScoreSummary
        # Return the best week's points per dart for the team.
        qs = self.get_queryset().prefetch_related("teamscoresummary_set", "players")
        qs = qs.annotate(best_week_ppd=Max(
                TeamScoreSummary.team_stats.filter(*args, **kwargs).filter(team=OuterRef("id")).values("best_week_doubles_ppd")
            )
        )
        return qs.filter(best_week_ppd__isnull=False)
        