from math import floor

from django.contrib.postgres.aggregates import StringAgg
from django.db import IntegrityError, models
from django.db.models import (
    Avg,
    Case,
    Count,
    ExpressionWrapper,
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
        return self.values("team__division", "team")

    def total_wins(self):
        return self.annotate(
            singles_pts=Sum("singles_points", default=0),
            doubles_pts=Sum("doubles_points", default=0),
        ).annotate(points=F("singles_pts") + F("doubles_pts"))

    def wins_by_team(self):
        from Members.models import Team

        return (
            self
            .annotate(
                team_name=Team.details.filter(pk=OuterRef("team")).values("team_name")
            ).values('team__division', 'team', 'team_name').total_wins()
        )

    def get_standings(self):
        from Members.models import Team

        return self.total_wins().annotate(
            team_name=Team.details.filter(pk=OuterRef("team")).values("team_name"),
            division=F("team__division"),
            week=F("match__week__week_number"),
        )

    def total_stars(self):
        return self.annotate(
            stars=Sum("total_stars", default=0),
        )

    def total_perfects(self):
        return self.annotate(
            perfects=Sum("total_perfects", default=0),
        )

    def highest_in(self):
        return self.annotate(
            max_high_in=Max("high_in", default=0),
        )

    def highest_out(self):
        return self.annotate(
            max_high_out=Max("high_out", default=0),
        )

    def weekly_ppd(self):
        return self.filter(
            Q(darts_thrown1__isnull=False) & Q(darts_thrown2__isnull=False)
        ).annotate(
            ppd=ExpressionWrapper(
                (Value(501.0) * Value(2) - F("score_left1") - F("score_left2"))
                / (F("darts_thrown1") + F("darts_thrown2")),
                output_field=models.FloatField(),
            )
        )

    def average_ppd(self):
        return self.weekly_ppd().values("player", "player__first_name", "player__last_name").annotate(avg_ppd=Avg(F("ppd")))

    def matches_played(self):
        return self.annotate(matches_played=Count("match_id", distinct=True))

    def average_stars_per_game(self):
        return (
            self.annotate(stars=Sum("total_stars",default=0))
            .values("player", "player__first_name", "player__last_name")
            .annotate(
                avg_spg=ExpressionWrapper(
                    F("stars") / (Count("match_id", distinct=True) * 10.0),
                    output_field=models.FloatField(),
                )
            )
        )

    def win_percentage(self):
        return (
            self.total_wins()
            .values("player", "player__first_name", "player__last_name")
            .annotate(
                win_percentage=ExpressionWrapper(
                    F("points") / (Count("match_id", distinct=True) * 10.0),
                    output_field=models.FloatField(),
                ),
            )
        )

    def rating(self):
        from Members.models import Team

        ppd_qs = Subquery(
            self.average_ppd().filter(player=OuterRef("player")).values("avg_ppd")
        )
        win_pct_qs = Subquery(
            self.win_percentage()
            .filter(player=OuterRef("player"))
            .values("win_percentage")
        )
        spg_qs = Subquery(
            self.average_stars_per_game()
            .filter(player=OuterRef("player"))
            .values("avg_spg")
        )
        team_name_qs = Subquery(
            Team.details.filter(pk=OuterRef("team")).values("team_name")
        )

        return (
            self.values(
                "team__division",
                "team",
                "player",
                "player__first_name",
                "player__last_name",
            )
            .annotate(
                avg_ppd=ppd_qs,
                win_percentage=win_pct_qs,
                avg_stars_per_game=spg_qs,
                team_name=team_name_qs,
            )
            .annotate(
                rating_score=ExpressionWrapper(
                    (Ln(Avg("avg_ppd")) * 3.5)
                    + (Avg("win_percentage") * 8.0)
                    + (Avg("avg_stars_per_game") * 5.0),
                    output_field=models.FloatField(),
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
            ),
        )

    def best_week_ppd(self):
        return (
            self.weekly_ppd().group_by_players()
            .annotate(
                best_week_singles_ppd=Max("ppd"),
            )
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
                    )
                    if qs.filter(player=player)
                    .values("player")
                    .aggregate(Avg("total_stars"))["total_stars__avg"]
                    is not None
                    else 0,
                )


class TeamScoreSummaryQuerySet(models.QuerySet):
    def with_names(self):
        from Members.models import Team

        return self.annotate(
            team_name=Team.details.filter(pk=OuterRef("team")).values("team_name"),
        )

    def weekly_doubles_ppd(self):
        return self.filter(Q(darts_thrown1__gte=1)&Q(darts_thrown2__gte=1)).annotate(
            weekly_doubles_ppd=(
                ((501.0 * 2) - (F("score_left1") + F("score_left2")))
                / (F("darts_thrown1") + F("darts_thrown2"))
            )
        )

    def avg_doubles_ppd(self):
        return (
            (
                self.weekly_doubles_ppd()
                .values("team")
                .annotate(avg_doubles_ppd=Avg(F("weekly_doubles_ppd")))
            )
            .with_names()
        )

    def best_501_game(self):
        return (
            self.values("team")
            .annotate(
                best_501_game=Least(
                    Min("darts_thrown1", filter=Q(score_left1=0)),
                    Min("darts_thrown2", filter=Q(score_left2=0)),
                    1000,
                )
            )
            .with_names()
        )

    def best_week_doubles_ppd(self):
        return (
            (
                self.weekly_doubles_ppd()
                .values("team")
                .annotate(best_week_doubles_ppd=Max(F("weekly_doubles_ppd")))
            )
            .with_names()
        )

    def team_rating(self, season):
        from Scores.models import ScoreSummary
        # Get player ratings for subquery expression
        ratings = ScoreSummary.stats.filter(match__week__season=season).filter(player__in=OuterRef('team__players')).rating().values('team').annotate(team_rating=(F('rating_score')))
        return (
            self.with_names()
            .values("team", "team__division", "team_name")
            .annotate(
                rating_score=Avg(ratings.values('team_rating')),
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

    def total_points(self, season):
        from Scores.models import ScoreSummary

        pts = (
            ScoreSummary.stats.filter(match__week__season=season, team=OuterRef("team"))
            .values("team")
            .annotate(singles_pts=Sum("singles_points"),
                      doubles_pts=Sum("doubles_points"))
            .annotate(total_pts=F("singles_pts") + F("doubles_pts"))
        )

        return (
            self
            .values("team")
            .annotate(
                points=Subquery(pts.values("total_pts")),
            ).with_names()
        )


class TeamScoreSummaryManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return (
            TeamScoreSummaryQuerySet(self.model, using=self._db)
            .select_related("team")
            .prefetch_related("team__players", "match__week__season")
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
