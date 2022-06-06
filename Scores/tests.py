from django.test import TestCase
from .models import *

class GameTestCase(TestCase):
    def setUp(self):
        BaseScore.objects.create(
            
        )
