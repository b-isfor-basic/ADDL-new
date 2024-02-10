from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from Schedule.models import Season, ScheduleWeek, Match

FIXTURES = [
    "./tests/fixtures/locations_data.json",
    "./tests/fixtures/members_data.json",
    "./tests/fixtures/schedule_data.json",
    "./tests/fixtures/scores_data.json",
]


class SeasonTestCase(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpTestData(cls):
        match_play_end_dt = timezone.now() + timedelta(days=84)
        cls.season = Season.objects.create(
            season_number=39,
            match_play_start_dt=timezone.now(),
            match_play_end_dt=match_play_end_dt,
        )
