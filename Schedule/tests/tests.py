from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from Schedule.models import Season, ScheduleWeek, Match


class SeasonTestCase(TestCase):
    fixtures = [
        "Locations/fixtures/data.json",
        "Members/fixtures/data.json",
        "Schedule/fixtures/data.json",
        "Scores/fixtures/data.json",
    ]

    @classmethod
    def setUpTestData(cls):
        match_play_end_dt = timezone.now() + timedelta(days=84)
        cls.season = Season.objects.create(
            season_number=39,
            match_play_start_dt=timezone.now(),
            match_play_end_dt=match_play_end_dt,
        )
