from django.urls import path, include
from .views import *

urlpatterns = [
    path("auth/", include("rest_framework.urls")),
    path("players/", PlayerList.as_view(), name="players_api"),
    path("teams/", team_list, name="teams_api"),
    path("players/sub/create/", create_sub, name="create_sub_api"),
    # path("divisions/", division_list, name="divisions_api"),
]
