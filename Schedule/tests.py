from datetime import timedelta

from django.utils import timezone
from django.test import TestCase

from .models import *

class SeasonTestCase(TestCase):
    def setUp(self):
        Season.objects.create(
            season_number = 39,
            match_play_start_dt = timezone.now(),
            match_play_end_dt = self.match_play_start_dt + timedelta(days=84),
            playoff_finals_dt = self.match_play_end_dt + timedelta(days=7),
        )