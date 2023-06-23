from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from Locations.models import Establishment
from Locations.views import EstablishmentListView, EstablishmentDetailView
from Members.models import Player


FIXTURES = [
    "Locations/fixtures/data.json",
    "Members/fixtures/data.json",
    "Schedule/fixtures/data.json",
    "Scores/fixtures/data.json",
]


class EstablishmentListViewTest(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = Player.objects.get(pk=6)

    def test_view_url_exists_at_desired_location(self):
        request = self.factory.get("/locations")
        response = EstablishmentListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        request = self.factory.get(reverse("all_areas"))
        response = EstablishmentListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_active_view_url_exists_at_desired_location(self):
        request = self.factory.get("/locations/active/")
        response = EstablishmentListView.as_view()(request, is_active=True)
        self.assertEqual(response.status_code, 200)

    def test_active_view_url_accessible_by_name(self):
        request = self.factory.get(reverse("active_areas"))
        response = EstablishmentListView.as_view()(request, is_active=True)
        self.assertEqual(response.status_code, 200)

    def test_active_view_queryset(self):
        request = self.factory.get(reverse("active_areas"))
        view = EstablishmentListView.as_view()(request, is_active=True)
        context = view.context_data
        queryset = view.context_data.get("all_areas")
        expected_queryset = Establishment.objects.filter(is_active=True).order_by(
            "number"
        )
        self.assertIn("all_areas", context)
        self.assertQuerysetEqual(expected_queryset, queryset)


class EstablishmentDetailViewTest(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = Player.objects.get(pk=6)

    def test_view_url_exists_at_desired_location(self):
        establishment = Establishment.objects.get(pk=1)
        request = self.factory.get("/locations/1")
        response = EstablishmentDetailView.as_view()(request, pk=establishment.pk)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        establishment = Establishment.objects.get(pk=1)
        request = self.factory.get(reverse("area_detail", args=[establishment.pk]))
        response = EstablishmentDetailView.as_view()(request, pk=establishment.pk)
        self.assertEqual(response.status_code, 200)

    def test_view_context(self):
        establishment = Establishment.objects.get(pk=1)
        request = self.factory.get(reverse("area_detail", args=[establishment.pk]))
        view = EstablishmentDetailView.as_view()(request, pk=establishment.pk)
        context = view.context_data
        queryset = view.context_data.get("area_divisions")
        expected_queryset = establishment.division_set.all()
        self.assertIn("area_detail", context)
        self.assertIn("area_divisions", context)
        self.assertQuerysetEqual(expected_queryset, queryset)
