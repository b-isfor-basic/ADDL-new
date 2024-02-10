from unittest import skipIf

from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls.exceptions import NoReverseMatch

from Locations.models import Establishment, Division
from Members.models import Player
from Schedule.models import Season

FIXTURES = [
    "./tests/fixtures/locations_data.json",
    "./tests/fixtures/members_data.json",
    "./tests/fixtures/schedule_data.json",
    "./tests/fixtures/scores_data.json",
]


class EstablishmentModelTestCase(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.loc1 = Establishment.objects.create(
            number=1,
            name="Test Establishment",
            shortName="Test Est",
            streetLine1="123 Main St",
            streetLine2="Suite 1",
            city="Atlanta",
            state="GA",
            zipCode=30303,
            generalManager="Test Manager",
            managerEmail="test@email.com",
            managerPhone="4045551234",
            is_active=True,
        )

        cls.loc2 = Establishment.objects.create(
            number=2,
            name="Test Establishment",
            streetLine1="321 Main St",
            city="Atlanta",
            state="GA",
            zipCode=30303,
            is_active=True,
        )

        cls.plyr1 = Player.objects.create(
            first_name="Test",
            last_name="Player",
            username="testplayer",
            password=make_password("testpassword"),
            email="testplayer@email.com",
            phoneNumber="+14045551111",
        )

        cls.div1 = Division.objects.create(
            area=cls.loc1,
            matchNight="Mon",
            playerFee=10,
            capacity=10,
            divisionManager=cls.plyr1,
        )

        cls.div2 = Division.objects.create(
            area=cls.loc2,
            matchNight="Tue",
            divisionManager=cls.plyr1,
        )

    def test_number_label(self):
        location = self.loc1
        field_label = location._meta.get_field("number").verbose_name
        self.assertEquals(field_label, "Area Number")

    def test_name_max_length(self):
        location = self.loc1
        max_length = location._meta.get_field("name").max_length
        self.assertEquals(max_length, 100)

    def test_shortName_max_length(self):
        location = self.loc1
        max_length = location._meta.get_field("shortName").max_length
        self.assertEquals(max_length, 35)

    def test_object_name_is_name(self):
        location = self.loc1
        expected_object_name = "Area 1 - Test Est"
        self.assertEquals(expected_object_name, str(location))

    def test_object_name_no_shortName(self):
        location = self.loc2
        location.shortName = None
        expected_object_name = "Area 2 - Test Establishment"
        self.assertEquals(expected_object_name, str(location))

    def test_get_address(self):
        location = self.loc1
        expected_address = "123 Main St\nSuite 1\nAtlanta, GA 30303"
        self.assertEquals(expected_address, location.get_address())

    def test_get_address_no_street2(self):
        location = self.loc2
        expected_address = "321 Main St\nAtlanta, GA 30303"
        self.assertEquals(expected_address, location.get_address())

    @skipIf(NoReverseMatch, "Feature not yet implemented")
    def test_get_reverse_url(self):
        location = self.loc1
        expected_url = "/locations/area/1/"
        self.assertEquals(expected_url, location.get_absolute_url())


class DivisionModelTestCase(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.loc1 = Establishment.objects.create(
            number=1,
            name="Test Establishment",
            shortName="Test Est",
            streetLine1="123 Main St",
            streetLine2="Suite 1",
            city="Atlanta",
            state="GA",
            zipCode=30303,
            generalManager="Test Manager",
            managerEmail="test@email.com",
            managerPhone="+14045551234",
            is_active=True,
        )

        cls.loc2 = Establishment.objects.create(
            number=2,
            name="Test Establishment",
            streetLine1="321 Main St",
            city="Atlanta",
            state="GA",
            zipCode=30303,
            is_active=True,
        )

        cls.plyr1 = Player.objects.create(
            first_name="Test",
            last_name="Player",
            username="testplayer",
            password=make_password("testpassword"),
            email="testplayer@email.com",
            phoneNumber="+14045551111",
        )

        cls.div1 = Division.objects.create(
            area=cls.loc1,
            matchNight="Mon",
            playerFee=10,
            capacity=10,
            divisionManager=cls.plyr1,
        )

        cls.div2 = Division.objects.create(
            area=cls.loc2,
            matchNight="Tue",
            divisionManager=cls.plyr1,
        )

    def test_object_name_is_name(self):
        division = self.div1
        expected_object_name = "Test Est - Mon"
        self.assertEquals(expected_object_name, str(division))

    def test_object_name_no_shortName(self):
        division = self.div2
        expected_object_name = "Test Establishment - Tue"
        self.assertEquals(expected_object_name, str(division))

    def test_division_manager(self):
        division = self.div1
        expected_manager = self.plyr1
        self.assertEquals(expected_manager, division.division_manager)

    def test_multiple_divisions_same_manager(self):
        division1 = self.div1
        division2 = self.div2
        division1.division_manager = self.plyr1
        division2.division_manager = self.plyr1
        expected_manager = self.plyr1
        self.assertEquals(expected_manager, division1.division_manager)
        self.assertEquals(expected_manager, division2.division_manager)

    def test_division_manager_removed(self):
        division = self.div1
        division.division_manager = None
        expected_manager = None
        self.assertEquals(expected_manager, division.division_manager)

    # Tests for detials Manager methods
    def test_division_num_active_teams(self):
        division = Division.details.get_num_active_teams(season=41).get(pk=1)
        expected_num = 8
        self.assertEquals(expected_num, division.num_teams)

    def test_division_with_names(self):
        division = Division.details.with_names().get(pk=1)
        expected_name = "Mazzy's 1 - Tues"
        self.assertEquals(expected_name, division.name)

    def test_division_with_names_no_shortName(self):
        division = self.div2
        expected_name = "Test Establishment - Tue"
        test_name = Division.details.with_names().get(pk=division.pk).name
        self.assertEquals(expected_name, test_name)
