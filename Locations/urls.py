from django.urls import path, re_path

from .views import EstablishmentListView, EstablishmentDetailView


urlpatterns = [
    path(
        "active/",
        EstablishmentListView.as_view(),
        name="active_areas",
        kwargs={"is_active": True},
    ),
    path("", EstablishmentListView.as_view(), name="all_areas"),
]
