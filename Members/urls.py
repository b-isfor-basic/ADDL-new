from django.urls import path, include
from .views import PlayerProfileView, PlayerCreateView

urlpatterns = [
    path("profile", PlayerProfileView, name="profile"),
    path("register", PlayerCreateView.as_view(), name="register"),
    path("", include("django.contrib.auth.urls")),
]
