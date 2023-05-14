from django.urls import include, path

from .views import PlayerCreateView, PlayerProfileView

urlpatterns = [
    path("profile", PlayerProfileView, name="profile"),
    path("register", PlayerCreateView.as_view(), name="register"),
    path("", include("django.contrib.auth.urls")),
]
