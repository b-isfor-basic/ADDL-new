from django.urls import path
from .views import PlayerProfileView, PlayerCreateView

urlpatterns = [
    path("profile", PlayerProfileView, name="profile"),
    path("register", PlayerCreateView.as_view(), name="register"),
]
