import unittest
import uuid

from django.test import TestCase

from Locations.models import Establishment, Division
from Schedule.models import Season, Match
from Members.models import Player, Team
from Scores.models import Scoreset, GameScore, Approval


class LocationsModelsTest(TestCase):
    def test_establishment_creation(self):
        # Create an Establishment
        establishment = Establishment.objects.create(
            number=1,
            name="Test Establishment",
            streetLine1="123 Test Street",
            city="Test City",
            state="GA",
            zipCode="30188",
            generalManager="Test Manager",
            managerEmail="test@email.com",
            managerPhone="1234567890",
        )

        # Verify that the establishment was created
        self.assertEqual(establishment.number, 1)
        self.assertEqual(establishment.name, "Test Establishment")
        self.assertEqual(establishment.streetLine1, "123 Test Street")
        self.assertEqual(establishment.city, "Test City")
        self.assertEqual(establishment.state, "GA")
        self.assertEqual(establishment.zipCode, "30188")
        self.assertEqual(establishment.generalManager, "Test Manager")
        self.assertEqual(establishment.managerEmail, "test@email.com")
        self.assertEqual(establishment.managerPhone, "1234567890")

    def test_establishment_get_address(self):
        # Create an Establishment
        establishment = Establishment.objects.create(
            number=1,
            name="Test Establishment",
            streetLine1="123 Test Street",
            city="Test City",
            state="GA",
            zipCode="30188",
            generalManager="Test Manager",
            managerEmail="test@email.com",
            managerPhone="1234567890",
        )
