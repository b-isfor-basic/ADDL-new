from datetime import timedelta

from django.utils import timezone
from django.test import TestCase

from .models import *

class SeasonTestCase(TestCase):
    def setUp(self):
        Season.objects.create(
            seasonNum = 39,
            startDate = timezone.now(),
            endDate = self.startDate + timedelta(days=84),
            playoffFinalsDate = self.endDate + timedelta(days=7),
        )