import uuid

from django.test import TestCase

from .models import *
from Schedule.models import Match

class ScoresetModelTest(TestCase):

    def setUp(self):
        #Get a Match
        self.match = Match.objects.first()
        #Get a Player
        self.player = self.match.homeTeam.player1
        #Get a Team
        self.team = self.match.homeTeam

    def test_scoreset_creation(self):

        # Create a Scoreset
        scoreset = Scoreset.details.create_new(
            player=self.player,
            team=self.team,
            match=self.match
        )

        # Verify that the scoreset was created
        self.assertEqual(scoreset.player, self.player)
        self.assertEqual(scoreset.team, self.team)
        self.assertEqual(scoreset.match, self.match)
        self.assertIsInstance(scoreset.id, uuid.UUID)

    def test_duplicate_scoreset_prevented(self):

        # Create a Scoreset
        scoreset = Scoreset.details.create_new(
            player=self.player,
            team=self.team,
            match=self.match
        )

        # Verify that the scoreset was not created
        self.assertRaises(scoreset.DuplicateScoresetError)