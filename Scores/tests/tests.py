import uuid

from django.test import TestCase

from Scores.models import ScoreSummary, TeamScoreSummary, Forfeit
from Schedule.models import Match


class ScoreSummaryModelTest(TestCase):
    fixtures = [
        "Locations/fixtures/data.json",
        "Members/fixtures/data.json",
        "Schedule/fixtures/data.json",
        "Scores/fixtures/data.json",
    ]

    @classmethod
    def setUpTestData(cls):
        # Get a Match
        cls.match = Match.objects.filter(scoresummary=None).first()
        # Get a Team from Match
        cls.team = cls.match.awayTeam
        # Get a Player
        cls.player = cls.team.players.first()
        # Create a dictionary of data to use for creating a scoresummary
        cls.scores = ScoreSummary.objects.create(
            match=cls.match,
            team=cls.team,
            player=cls.player,
            darts_thrown1=20,
            score_left1=0,
            darts_thrown2=30,
            score_left2=10,
            total_stars=10,
            total_perfects=1,
            singles_points=4,
            doubles_points=6,
            high_in=100,
            high_out=100,
        )

    def test_duplicate_scoresummary_prevented(self):
        with self.assertRaises(Exception):
            test_scoresummary = self.scores
            test_scoresummary2 = ScoreSummary.objects.create(
                match=test_scoresummary.match,
                team=test_scoresummary.team,
                player=test_scoresummary.player,
                darts_thrown1=test_scoresummary.darts_thrown1,
                score_left1=test_scoresummary.score_left1,
                darts_thrown2=test_scoresummary.darts_thrown2,
                score_left2=test_scoresummary.score_left2,
                total_stars=test_scoresummary.total_stars,
                total_perfects=test_scoresummary.total_perfects,
                singles_points=test_scoresummary.singles_points,
                doubles_points=test_scoresummary.doubles_points,
                high_in=test_scoresummary.high_in,
                high_out=test_scoresummary.high_out,
            )
            test_scoresummary2.save()

    def test_scoresummary_weekly_average_ppd(self):
        data = self.scores
        points_scored = 1001.0 - data.score_left1 - data.score_left2
        darts_thrown = data.darts_thrown1 + data.darts_thrown2
        average = points_scored / darts_thrown
        self.assertEqual(data.singles_weekly_ppd, average)

    def test_scoresummary_total_points(self):
        data = self.scores
        self.assertEqual(data.total_points, data.singles_points + data.doubles_points)
