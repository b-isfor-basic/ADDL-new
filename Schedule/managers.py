from collections.abc import Iterable, Sequence
from datetime import datetime as dt
from datetime import timedelta

from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import (
    Case,
    Count,
    F,
    Manager,
    Max,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Sum,
    Value,
    When,
    FloatField,
    ExpressionWrapper,
)
from django.db.models.functions import JSONObject
from django.db.models.lookups import GreaterThan, Exact
from django.utils import timezone


class ScheduleManager(Manager):
    pass


class MatchQuerySet(QuerySet):
    def weekly_ppd(self, group):
        if group == "player":
            table = "scoresummary"
        elif group == "team":
            table = "teamscoresummary"
        return (
            self.values(party=F(f"{table}__{group}"), week_num=F("week__week_number"))
            .annotate(
                ppd=ExpressionWrapper(
                    (
                        Value(501.0) * Value(2)
                        - F(f"{table}__score_left1")
                        - F(f"{table}__score_left2")
                    )
                    / (F(f"{table}__darts_thrown1") + F(f"{table}__darts_thrown2")),
                    output_field=FloatField(),
                )
            )
            .filter(ppd__isnull=False)
        )

    def average_ppd(self, group):
        return (
            self.weekly_ppd(group)
            .values("party")
            .annotate(avg_ppd=Sum("ppd") / Count("week_num"))
        )

    def best_ppd(self, group):
        return self.weekly_ppd(group).values("party").annotate(best_ppd=Max("ppd"))

    def total_points(self, group):
        q = f"scoresummary__{group}"
        return (
            self.values(q)
            .annotate(
                singles_wins=Sum("scoresummary__singles_points", default=0),
                doubles_wins=Sum("scoresummary__doubles_points", default=0),
            )
            .annotate(
                total_points=F("singles_wins") + F("doubles_wins"),
            )
        )

    def weekly_points_by_division(self):
        return (
            self.values("week__division", "week__week_number", "scoresummary__team")
            .annotate(
                points=Sum("scoresummary__singles_points", default=0)
                + Sum("scoresummary__doubles_points", default=0)
            )
            .order_by("week__division", "week__week_number")
        )


class MatchManager(Manager.from_queryset(MatchQuerySet)):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("awayTeam", "homeTeam", "week")
            .prefetch_related(
                "scoresummary_set",
                "awayTeam__players",
                "homeTeam__players",
                "week__season",
                "teamscoresummary_set",
            )
        )

    def with_names(self):
        from Members.models import Team

        qs = self.get_queryset()
        return qs.annotate(
            away_team=Subquery(
                Team.details.filter(id=OuterRef("awayTeam")).values("team_name")
            ),
            home_team=Subquery(
                Team.details.filter(id=OuterRef("homeTeam")).values("team_name")
            ),
        )

    def by_season(self, season):
        return self.get_queryset().filter(week__season__season_number=season)

    def by_division(self, division):
        return self.get_queryset().filter(week__division=division)

    def by_player(self, player):
        return self.get_queryset().filter(
            Q(awayTeam__players__contains=player)
            | Q(homeTeam__players__contains=player)
        )

    def status(self):
        from Scores.models import ScoreSummary

        qs = self.with_names()
        scores = (
            ScoreSummary.objects.all()
            .values("match", "team")
            .annotate(
                points=Sum("singles_points", default=0)
                + Sum("doubles_points", default=0)
            )
        )

        return qs.annotate(
            home_score=Subquery(
                scores.filter(match=OuterRef("id"), team=OuterRef("homeTeam")).values(
                    "points"
                )
            ),
            away_score=Subquery(
                scores.filter(match=OuterRef("id"), team=OuterRef("awayTeam")).values(
                    "points"
                )
            ),
        ).annotate(
            status=Case(
                When(
                    Exact(F("forfeit__team"), F("homeTeam")),
                    then=Value('Away <span class="pl-1 text-rose-400 text-xs align-center text-center">F</span>'),
                ),
                When(
                    Exact(F("forfeit__team"), F("awayTeam")),
                    then=Value('Home <span class="pl-1 text-rose-400 text-xs align-center text-center">F</span>'),
                ),
                When(
                    Exact(F("home_score"), 0) & Exact(F("away_score"), 0),
                    then=Value("Missing"),
                ),
                When(GreaterThan(F("home_score"), F("away_score")), then=Value("Home")),
                When(GreaterThan(F("away_score"), F("home_score")), then=Value("Away")),
                When(Exact(F("home_score"), 10), then=Value("Draw")),
                default=Value("Missing"),
            )
        )


class SeasonManager(Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("scheduleweek_set", "scheduleweek_set__match_set")
        )

    def active(self):
        season_start_before_today = Q(match_play_start_dt__lte=timezone.now())
        season_end_after_today = Q(match_play_end_dt__gte=timezone.now())

        if (
            self.get_queryset()
            .filter(season_start_before_today & season_end_after_today)
            .exists()
        ):
            return (
                self.get_queryset()
                .filter(season_start_before_today & season_end_after_today)
                .first()
            )
        return self.get_queryset().latest("match_play_start_dt")

    def schedule(self):
        from Locations.models import Division
        from Schedule.models import ScheduleWeek, Match

        qs = self.get_queryset()
        season_weeks = ScheduleWeek.objects.filter(season=OuterRef("id")).order_by(
            "division", "week_number"
        )
        matches = Match.details.status().values(
            json=JSONObject(
                id=F("id"),
                home_team=F("home_team"),
                away_team=F("away_team"),
                status=F("status"),
            )
        )

        return qs.annotate(
            division=F("divisions"),
        ).annotate(
            div_name=Subquery(
                Division.details.with_names()
                .filter(id=OuterRef("division"))
                .values("name")
            ),
            weeks=ArraySubquery(
                season_weeks.filter(division=OuterRef("division"))
                .annotate(week=F("id"))
                .annotate(
                    match_qs=ArraySubquery(matches.filter(week__id=OuterRef("week")))
                )
                .values(
                    matches=JSONObject(
                        week_num=F("week_number"),
                        date=F("match_date"),
                        matches=F("match_qs"),
                    )
                )
            ),
        )
