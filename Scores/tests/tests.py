import uuid

from django.test import TestCase

from Scores.models import ScoreSummary, TeamScoreSummary, Approval, Forfeit
from Schedule.models import Match


class ScoreSummaryModelTest(TestCase):
    @classmethod
    def setUp(self):
        # Get a Match
        self.match = Match.objects.last()
        # Get a Team from Match
        self.team = self.match.awayTeam
        # Get a Player
        self.player = self.team.player1
        # Create a dictionary of data to use for creating a scoresummary
        self.data = {
            "match": self.match,
            "team": self.team,
            "player": self.player,
            "darts_thrown1": 20,
            "score_left1": 0,
            "darts_thrown2": 30,
            "score_left2": 10,
            "total_stars": 10,
            "total_perfects": 1,
            "singles_points": 4,
            "doubles_points": 6,
            "high_in": 100,
            "high_out": 100,
        }

    def test_scoresummary_creation(self):
        # Create a scoresummary
        test_scoresummary = ScoreSummary.objects.create(self.data)
        test_scoresummary.save()
        # Verify that the scoresummary was created with matching field data
        for key, value in self.data.items():
            self.assertEqual(getattr(test_scoresummary, key), value)
            self.assertIsInstance(id, uuid.UUID)
        # Verify that the scoresummary was created in the database
        self.assertEqual(ScoreSummary.objects.last(), test_scoresummary)

    def test_duplicate_scoresummary_prevented(self):
        with self.assertRaises(Exception):
            test_scoresummary = ScoreSummary.objects.create(self.data)
            test_scoresummary.save()
            test_scoresummary2 = ScoreSummary.objects.create(self.data)
            test_scoresummary2.save()

    def test_scoresummary_deletion(self):
        test_scoresummary = ScoreSummary.objects.create(self.data)
        test_scoresummary.save()
        test_scoresummary.delete()
        self.assertEqual(ScoreSummary.objects.count(), 0)

    def test_scoresummary_update(self):
        test_scoresummary = ScoreSummary.objects.create(self.data)
        test_scoresummary.save()
        test_scoresummary.total_stars = 20
        test_scoresummary.save()
        self.assertEqual(test_scoresummary.total_stars, 20)

    def test_scoresummary_str(self):
        test_scoresummary = ScoreSummary.objects.create(self.data)
        test_scoresummary.save()
        self.assertEqual(str(test_scoresummary), f"{self.player} - {self.match}")

    def test_scoresummary_get_absolute_url(self):
        test_scoresummary = ScoreSummary.objects.create(self.data)
        test_scoresummary.save()
        self.assertEqual(
            test_scoresummary.get_absolute_url(),
            f"/scores/{self.match.id}/{self.player.id}/",
        )
