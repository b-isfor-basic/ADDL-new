from datetime import datetime as dt
from datetime import timedelta

from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import Case, F, Manager, OuterRef, Q, Subquery, Sum, Value, When
from django.db.models.functions import JSONObject
from django.db.models.lookups import GreaterThan, IsNull, Exact
from django.utils import timezone


class ScheduleManager(Manager):
    # TODO: This is not functional yet. Needs to be revised.
    def create(self, season):
        from .models import Match, Season

        season = Season.objects.get(pk=season)
        divisions = season.divisions.all()
        start_dt = season.match_play_start_dt
        end_dt = season.match_play_end_dt

        def get_weeks(start_dt, end_dt, season, division):
            match_night = dt.strptime(division.matchNight, "%A").weekday()
            start_dt = dt.date(start_dt) + timedelta(
                days=match_night.weekday() - start_dt.weekday()
            )
            weeks = []
            week_number = 1
            current_dt = dt.date(start_dt)
            print(match_night, start_dt, end_dt, weeks)
            while dt.date(current_dt) <= dt.date(end_dt):
                weeks.append(
                    super().create(
                        week=week_number,
                        date=dt.date(current_dt),
                        season=season,
                        division=division,
                    )
                )
                current_dt += timedelta(days=7)
                week_number += 1
            return weeks

        for division in divisions:
            if division.scheduleweek_set.filter(season=season).exists():
                return print(f"Schedule for {season} and {division} already exists.")
            weeks = get_weeks(start_dt, end_dt, season, division)
            for week in weeks:
                week.save()


class MatchManager(Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("awayTeam", "homeTeam")
            .prefetch_related(
                "scoresummary_set", "awayTeam__players", "homeTeam__players"
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
        scores = ScoreSummary.objects.all().values('match', 'team').annotate(
                points=Sum('singles_points', default=0) + Sum('doubles_points', default=0)
            )
        
        return qs.annotate(
            home_score=Subquery(scores.filter(match=OuterRef('id'), team=OuterRef('homeTeam')).values('points')),
            away_score=Subquery(scores.filter(match=OuterRef('id'), team=OuterRef('awayTeam')).values('points'))
        ).annotate(status=Case(
            When(Exact(F('home_score'), 0) & Exact(F('away_score'), 0), then=Value("Missing")),
            When(GreaterThan(F('home_score'), F('away_score')), then=Value("Home")),
            When(GreaterThan(F('away_score'), F('home_score')), then=Value("Away")),
            When(Exact(F('home_score'), 10), then=Value("Draw")),
            default=Value("Missing")
        ))
        
        

class SeasonManager(Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("scheduleweek_set", "scheduleweek_set__match_set")
        )

    def get_active(self):
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
        from .models import ScheduleWeek, Match
        from Locations.models import Division

        qs = self.get_queryset()
        season_weeks = ScheduleWeek.objects.filter(season=OuterRef('id'))
        matches = Match.details.status().values(json=JSONObject(id=F('id'), home_team=F('home_team'), away_team=F('away_team'), status=F('status')))

        return qs.annotate(
            division=F('divisions'),
        ).annotate(
            div_name=Subquery(Division.details.named().filter(id=OuterRef('division')).values('name')),
            weeks=ArraySubquery(
                season_weeks.filter(
                    division=OuterRef('division')
                ).annotate(
                    week=F('id')
                ).annotate(
                    match_qs=ArraySubquery(
                        matches.filter(
                            week__id=OuterRef('week')
                        )
                    )
                ).values(matches=JSONObject(
                    week_num=F('week_number'),
                    date=F('match_date'),
                    matches=F('match_qs')
                ))
            )
        )
