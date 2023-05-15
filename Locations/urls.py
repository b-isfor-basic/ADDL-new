from django.urls import path

from .views import EstablishmentListView


urlpatterns = [
    path("", EstablishmentListView.as_view(), name="all_areas"),
]
