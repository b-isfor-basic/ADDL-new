from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.SeasonDetailView, name="schedule"),
    re_path(r"^(?P<query>\w+)/$", views.SeasonDetailView, name="schedule"),
]
