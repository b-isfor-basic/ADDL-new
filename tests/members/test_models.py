from django.contrib.auth.hashers import make_password
from django.test import TestCase

from Members.models import Player, Team


FIXTURES = [
    "./tests/fixtures/locations_data.json",
    "./tests/fixtures/members_data.json",
    "./tests/fixtures/schedule_data.json",
    "./tests/fixtures/scores_data.json",
]


class PlayerModelTestCase(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpTestData(cls):
        cls.player = Player.objects.get(pk=4)
        cls.player2 = Player.objects.create(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test.user@email.com",
            password=make_password(None),
            phoneNumber="+14045551234",
        )

    def test_unique_username(self):
        plyr = self.player2
        plyr2 = Player.objects.create(
            username=plyr.username,
            first_name="Test",
            last_name="User",
            password=make_password(None),
        )
        self.assertRaises(ValueError, plyr2)

    def test_unique_email(self):
        plyr = self.player2
        plyr2 = Player.objects.create(
            username="testuser2",
            first_name="Test",
            last_name="User",
            email=plyr.email,
            password=make_password(None),
        )
        self.assertRaises(ValueError, plyr2)

    def test_player_str(self):
        plyr = self.player
        self.assertEqual(str(plyr), f"{plyr.first_name} {plyr.last_name}")

    def test_player_queryset_ordering(self):
        qs = Player.objects.all().order_by("first_name", "last_name")
        self.assertQuerysetEqual(qs, Player.objects.all())


class TeamModelTestCase(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpTestData(cls):
        cls.plyr1 = Player.objects.create(
            username="testuser1",
            first_name="Test",
            last_name="User",
            password=make_password(None),
        )
        cls.plyr2 = Player.objects.create(
            username="testuser2",
            first_name="Test",
            last_name="User",
            password=make_password(None),
        )
        cls.team = Team.objects.create(
            division=1, season=3, players=[cls.plyr1, cls.plyr2]
        )

    def test_team_str(self):
        names = [plyr.last_name for plyr in self.team.players.all()]
        team_name = "/".join(names)
        self.assertEqual(str(self.team), team_name)
