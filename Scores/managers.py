from math import floor

from django.contrib.postgres.aggregates import StringAgg
from django.db import IntegrityError, models
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
    Window,
)
from django.db.models.functions import DenseRank, Least, Ln
from django.db.models.lookups import GreaterThanOrEqual, LessThan, LessThanOrEqual



class PlayerScoreSummaryQuerySet(models.QuerySet):
    def group_by_players(self):
        return self.values("player", "player__first_name", "player__last_name")

    def group_by_teams(self):
        return self.annotate(
            team_name=StringAgg(
                "team__players__last_name", delimiter="/", distinct=True
            )
        ).values("team", "team_name")
    
    def rank_desc(self, stat=""):
        return self.annotate(
            rank=Window(
                expression=DenseRank(),
                order_by=F(stat).desc(),
            )
        )
    
    def rank_asc(self, stat=""):
        return self.annotate(
            rank=Window(
                expression=DenseRank(),
                order_by=F(stat).asc(),
            )
        )

    def total_wins(self):
        return self.annotate(
            singles_pts=Sum("singles_points", default=0),
            doubles_pts=Sum("doubles_points", default=0),
            points=F("singles_pts") + F("doubles_pts"),
        )

    def total_stars(self):
        return self.annotate(stars=Sum("total_stars", default=0))

    def total_perfects(self):
        return self.annotate(perfects=Sum("total_perfects", default=0))

    def highest_in(self):
        return self.annotate(max_high_in=Max("high_in", default=0))

    def highest_out(self):
        return self.annotate(max_high_out=Max("high_out", default=0))

    def weekly_ppd(self):
        return self.annotate(
            weekly_ppd=Case(
                When(
                    Q(darts_thrown1__isnull=True) | Q(darts_thrown2__isnull=True),
                    then=None,
                ),
                When(
                    darts_thrown1__isnull=False,
                    darts_thrown2__isnull=False,
                    then=((501.0 * 2) - (F("score_left1") + F("score_left2")))
                    / (F("darts_thrown1") + F("darts_thrown2")),
                ),
                default=(None),
                output_field=models.FloatField(),
            ),
        )

    def average_ppd(self):
        return (
            self.weekly_ppd()
            .values("player", "player__first_name", "player__last_name")
            .annotate(avg_ppd=Avg(F("weekly_ppd")))
        )

    def matches_played(self):
        return self.annotate(matches_played=Count("match_id", distinct=True))

    def average_stars_per_game(self):
        return (
            self.matches_played()
            .total_stars()
            .annotate(
                avg_stars_per_game=Case(
                    When(
                        Q(matches_played=0),
                        then=None,
                    ),
                    When(
                        Q(matches_played__gt=0),
                        then=(F("stars") / (F("matches_played") * 10.0)),
                    ),
                    default=0,
                    output_field=models.FloatField(),
                )
            )
        )

    def win_percentage(self):
        return (
            self.matches_played()
            .total_wins()
            .annotate(
                win_percentage=Case(
                    When(
                        matches_played=0,
                        then=None,
                    ),
                    default=(F("points") / (F("matches_played") * 10.0)),
                    output_field=models.FloatField(),
                )
            )
        )

    def rating(self):
        return (
            self.weekly_ppd()
            .annotate(weekly_ppd=F("weekly_ppd"))
            .group_by_players()
            .average_ppd()
            .win_percentage()
            .average_stars_per_game()
            .annotate(
                rating_score=(
                    (Ln(F("weekly_ppd")) * 3.5)
                    + (F("win_percentage") * 8.0)
                    + (F("avg_stars_per_game") * 5.0)
                ),
                rating=Case(
                    When(LessThanOrEqual(F("rating_score"), 10.50), then=Value("E")),
                    When(LessThan(F("rating_score"), 12.20), then=Value("D")),
                    When(LessThan(F("rating_score"), 15.40), then=Value("C")),
                    When(LessThan(F("rating_score"), 18.80), then=Value("B")),
                    When(LessThan(F("rating_score"), 22.50), then=Value("A")),
                    When(
                        GreaterThanOrEqual(F("rating_score"), 22.50), then=Value("AA")
                    ),
                ),
            )
        )

    def avg_points_per_match(self):
        return (
            self.total_wins()
            .matches_played()
            .aggregate(avg_pts_per_match=(F("points") / F("matches_played")))
        )

    def best_501_game(self):
        return self.annotate(
            best_501_game=Least(
                Min("darts_thrown1", filter=Q(score_left1=0)),
                Min("darts_thrown2", filter=Q(score_left2=0)),
                1000,
            )
        )

    def best_week_ppd(self):
        return (
            self.weekly_ppd()
            .group_by_players()
            .annotate(best_week_singles_ppd=Max("weekly_ppd"))
        )


class PlayerScoreSummaryManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return (
            PlayerScoreSummaryQuerySet(self.model, using=self._db)
            .filter(*args, **kwargs)
            .select_related("player", "team")
        )

    def _adjusted_player_pts(self, team_total_pts, player_total_points):
        return round(player_total_points * 11 / team_total_pts)

    def create_record_for_forfeit(self, match, team):
        season = match.week.season
        qs = self.get_queryset().filter(match__week__season=season, team=team)

        team_average_points_per_match = qs.values("team").avg_points_per_match()[
            "avg_pts_per_match"
        ]
        player_total_points = qs.values("player").total_wins().order_by("-points")

        if team_average_points_per_match <= 11:
            if player_total_points[0]["points"] == player_total_points[1]["points"]:
                higher_scoring_player = (
                    qs.values("player").rating().order_by("-rating_score")[0]["player"]
                )
            else:
                higher_scoring_player = player_total_points[0]["player"]

            for player in team.players.all():
                player_adjusted_scored_points = (
                    6 if player == higher_scoring_player else 5
                )
                yield super().create(
                    match=match,
                    team=team,
                    player=player,
                    is_sub=False,
                    singles_points=2 if player_adjusted_scored_points == 5 else 3,
                    doubles_points=3,
                    total_stars=floor(
                        qs.filter(player=player)
                        .values("player")
                        .aggregate(Avg("total_stars"))["total_stars__avg"]
                    ),
                )
        else:
            for player in team.players.all():
                yield super().create(
                    match=match,
                    team=team,
                    player=player,
                    is_sub=False,
                    singles_points=round(
                        qs.filter(player=player)
                        .values("player")
                        .aggregate(Avg("singles_points"))["singles_points__avg"]
                    ),
                    doubles_points=round(
                        qs.filter(player=player)
                        .values("player")
                        .aggregate(Avg("doubles_points"))["doubles_points__avg"]
                    ),
                    total_stars=floor(
                        qs.filter(player=player)
                        .values("player")
                        .aggregate(Avg("total_stars"))["total_stars__avg"]
                    ),
                )


class TeamScoreSummaryQuerySet(models.QuerySet):
    def get(self, *args, **kwargs):
        return (
            self.select_related("team")
            .prefetch_related("team__players", "match__week__season")
            .filter(*args, **kwargs)
        )

    def weekly_doubles_ppd(self):
        return self.annotate(
            weekly_doubles_ppd=(
                ((501.0 * 2) - (F("score_left1") + F("score_left2")))
                / (F("darts_thrown1") + F("darts_thrown2"))
            )
        )

    def avg_doubles_ppd(self):
        return (
            self.weekly_doubles_ppd()
            .values("team", "team_name")
            .annotate(avg_doubles_ppd=Avg(F("weekly_doubles_ppd")))
        ).filter(avg_doubles_ppd__isnull=False)

    def best_501_game(self):
        return self.values("team", "team_name").annotate(
            best_501_game=Least(
                Min("darts_thrown1", filter=Q(score_left1=0)),
                Min("darts_thrown2", filter=Q(score_left2=0)),
                1000,
            )
        ).filter(best_501_game__isnull=False)

    def best_week_doubles_ppd(self):
        return (
            self.weekly_doubles_ppd()
            .values("team", "team_name")
            .annotate(best_week_doubles_ppd=Max(F("weekly_doubles_ppd")))
        ).filter(best_week_doubles_ppd__isnull=False)

    def team_rating(self, *season):
        from Scores.models import ScoreSummary

        # Get player ratings for subquery expression
        player_rating_avg = (
            ScoreSummary.stats.filter(
                Q(
                    match__week__season=self.values_list(
                        "match__week__season", flat=True
                    )[0]
                )
                & Q(player__in=OuterRef("team__players"))
            )
            .values("team", "player")
            .rating()
        )

        return self.values("team", "team_name").annotate(
            team_rating_score=Avg(player_rating_avg.values("rating_score")),
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
    
    from django.db.models import Sum, Subquery, OuterRef

    class TeamScoreSummaryQuerySet(models.QuerySet):
        def total_wins(self, *args, **kwargs):
            from .models import ScoreSummary
            pts = ScoreSummary.stats.values('team').annotate(points=Sum("singles_points", default=0) + Sum("doubles_points", default=0))
            return self.annotate(
                team_name=StringAgg(
                    "team__players__last_name", delimiter="/", distinct=True
                ),
                points=Sum(Subquery(pts.get(team=OuterRef("team"))).points)
            )

    def all_stats(self):
        return (
            self.annotate(
                team_name=StringAgg(
                    "team__players__last_name", delimiter="/", distinct=True
                )
            )
            .weekly_doubles_ppd()
            .values("team", "team_name")
            .avg_doubles_ppd()
            .team_rating()
            .best_week_doubles_ppd()
            .best_501_game()
        )


class TeamScoreSummaryManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return (
            TeamScoreSummaryQuerySet(self.model, using=self._db)
            .select_related("team")
            .prefetch_related("team__players", "match__week__season")
            .filter(*args, **kwargs)
            .annotate(
                team_name=StringAgg(
                    "team__players__last_name", delimiter="/", distinct=True
                )
            )
        )


class ForfeitManager(models.Manager):
    def create(self, **kwargs):
        """
        Forfeit matches cannot have existing scoresummary/teamscoresummary records.
        After registering a forfeit, the winning team's scoresummary record will be
        automatically generated.

        If the winning team's average points per match is less than 11, the team will
        receive 5 points for singles games and 6 points for doubles games, divided
        between the players proportionate to their season win average.

        If the average is greater than 11, the winning team will receive the average of
        their singles and doubles points for the season.
        """
        from Schedule.models import Match
        from Scores.models import ScoreSummary

        match = kwargs.get("match")
        forfeit_team_id = kwargs.get("team")

        # Check if match already has scoresummary or teamscoresummary record for team
        if (
            match.scoresummary_set.exists() == True
            or match.teamscoresummary_set.exists() == True
        ):
            raise IntegrityError(
                "Match already has scoresummary or teamscoresummary record."
            )

        # Determine winning team and create scoresummary record
        if match.homeTeam == forfeit_team_id:
            winning_team = match.awayTeam
        else:
            winning_team = match.homeTeam

        if winning_team is not None:
            winning_scores = ScoreSummary.stats.create_record_for_forfeit(
                match, winning_team
            )
            for score in winning_scores:
                score.save()

        return super().create(**kwargs)
