from datetime import timedelta, datetime as dt

from django.db.models import Manager, Q, Sum, Count, Avg
from django.utils import timezone

from Locations.models import Division


class ScheduleManager(Manager):
    # TODO: This is not functional yet. Needs to be revised.
    def create(self, season):
        
        from .models import Season, Match
        
        season = Season.objects.get(pk=season)
        divisions = season.divisions.all()
        start_dt = season.match_play_start_dt
        end_dt = season.match_play_end_dt
        
        def get_weeks(start_dt, end_dt, season, division):
            match_night = dt.strptime(division.matchNight, '%A').weekday()
            start_dt = dt.date(start_dt) + timedelta(days=match_night.weekday() - start_dt.weekday())
            weeks = []
            week_number = 1
            current_dt = dt.date(start_dt)
            print(match_night, start_dt, end_dt, weeks)
            while dt.date(current_dt) <= dt.date(end_dt):
                weeks.append(super().create(week=week_number, date=dt.date(current_dt), season=season, division=division))
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
    def by_season(self, season):
        return self.get_queryset().filter(week__season__season_number=season)

    def by_division(self, division):
        return self.get_queryset().filter(week__division=division)

    def by_player(self, player):
        return self.get_queryset().filter(Q(awayTeam=player.team) | Q(homeTeam=player.team))


class SeasonManager(Manager):
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

        