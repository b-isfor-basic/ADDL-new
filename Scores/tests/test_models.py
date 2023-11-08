import uuid

from django.db import IntegrityError
from django.db.models import Count
from django.test import TestCase

from Scores.models import ScoreSummary, TeamScoreSummary, Forfeit
from Schedule.models import Match

FIXTURES = [
    "Locations/fixtures/data.json",
    "Members/fixtures/data.json",
    "Schedule/fixtures/data.json",
    "Scores/fixtures/data.json",
]

class ScoreSummaryModelTest(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpTestData(cls):
        # Get a Match
        cls.match = Match.objects.filter(scoresummary=None).first()
        # Get a Team from Match
        cls.team = cls.match.awayTeam
        # Get a Player
        cls.player = cls.team.players.first()
        # Create a dictionary of data to use for creating a scoresummary
        cls.scores = ScoreSummary(
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
        test_scoresummary = self.scores
        with self.assertRaises(IntegrityError):
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

    def test_scoresummary_weekly_average_ppd(self):
        data = self.scores
        points_scored = 1001.0 - data.score_left1 - data.score_left2
        darts_thrown = data.darts_thrown1 + data.darts_thrown2
        average = points_scored / darts_thrown
        return self.assertEqual(data.singles_weekly_ppd, average)

    def test_scoresummary_total_points(self):
        data = self.scores
        return self.assertEqual(data.total_points, data.singles_points + data.doubles_points)
    

class ScoreSummaryManagerTest(TestCase):
    def test_get_queryset(self):
        from Scores.models import ScoreSummary

        qs = ScoreSummary.stats.get_queryset()
        return self.assertEqual(qs.count(), 0)


class TeamScoreSummaryModelTest(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpTestData(cls):
        # Get a Match
        cls.match = Match.objects.filter(scoresummary=None).first()
        # Get a Team from Match
        cls.team = cls.match.awayTeam
        # Create a dictionary of data to use for creating a scoresummary
        cls.scores = TeamScoreSummary.objects.create(
            match=cls.match,
            team=cls.team,
            darts_thrown1=20,
            score_left1=0,
            darts_thrown2=30,
            score_left2=10,
        )

    def test_duplicate_scores_prevented(self):
        test_scores = self.scores
        with self.assertRaises(IntegrityError):
            test_scores2 = TeamScoreSummary.objects.create(
                match=test_scores.match,
                team=test_scores.team,
                darts_thrown1=test_scores.darts_thrown1,
                score_left1=test_scores.score_left1,
                darts_thrown2=test_scores.darts_thrown2,
                score_left2=test_scores.score_left2,
            )

    def test_scores_weekly_average_ppd(self):
        data = self.scores
        points_scored = 1001.0 - data.score_left1 - data.score_left2
        darts_thrown = data.darts_thrown1 + data.darts_thrown2
        average = round(points_scored / darts_thrown, 4)
        return self.assertEqual(data.weekly_ppd, average)


class ForfeitModelTest(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpTestData(cls):
        # Get a Match
        cls.match = Match.objects.filter(scoresummary=None).first()
        # Get a Team from Match
        cls.team = cls.match.awayTeam
        # Create a dictionary of data to use for creating a scoresummary
        cls.forfeit = Forfeit.details.create(
            match=cls.match,
            team=cls.team,
        )

    def test_duplicate_forfeit_prevented(self):
        test_forfeit = self.forfeit
        with self.assertRaises(IntegrityError):
            test_forfeit2 = Forfeit.objects.create(
                match=test_forfeit.match,
                team=test_forfeit.team,
            )

    def test_forfeit_match_cannot_have_player_score(self):
        self.match = ScoreSummary.objects.first().match
        with self.assertRaises(IntegrityError):
            Forfeit.details.create(
                match=self.match,
                team=self.match.homeTeam,
            )

    def test_forfeit_match_cannot_have_team_score(self):
        self.match = TeamScoreSummary.objects.first().match
        with self.assertRaises(IntegrityError):
            Forfeit.details.create(
                match=self.match,
                team=self.match.homeTeam,
            )      

    def test_creating_forfeit_creates_winning_team_score(self):
        test_forfeit = self.forfeit
        return (
            self.assertEqual(test_forfeit.match.scoresummary_set.count(), 2),
            self.assertIn(
                test_forfeit.match.homeTeam.id,
                test_forfeit.match.scoresummary_set.all().values_list(
                    "team", flat=True
                ),
            ),
            self.assertNotIn(
                test_forfeit.match.awayTeam,
                test_forfeit.match.scoresummary_set.all().values_list(
                    "team", flat=True
                ),
            ),
        )
