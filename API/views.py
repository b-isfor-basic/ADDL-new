from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import requires_csrf_token

from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Members.models import Player, Team
from .serializers import PlayerSerializer, SubstituteSerializer, TeamSerializer


@api_view(["GET"])
@login_required
@requires_csrf_token
def player_list(request):
    if request.method == "GET":
        objects = Player.objects.all()
        serializer = PlayerSerializer(objects, many=True)
        return Response(serializer.data)


@api_view(["POST"])
@login_required
@requires_csrf_token
def create_sub(request):
    if request.method == "POST":
        serializer = SubstituteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@login_required
@requires_csrf_token
def sub_list(request, season):
    if request.method == "GET":
        objects = Player.objects.all().prefetch_related(
            "scoresummary_set",
            "scoresummary_set__match",
            "scoresummary_set__match__week",
        )
        objects = objects.filter(scoresummary__match__week__season=season).filter(
            scoresummary__is_sub=True
        )
        serializer = SubstituteSerializer(objects, many=True)
        return Response(serializer.data)


@api_view(["GET"])
@login_required
@requires_csrf_token
def team_list(request):
    if request.method == "GET":
        objects = Team.objects.all().prefetch_related("players")
        serializer = TeamSerializer(objects, many=True)
        return Response(serializer.data)


class PlayerList(generics.ListCreateAPIView):
    queryset = Player.objects.all()
    serializer_class = SubstituteSerializer
    permission_classes = [IsAuthenticated]
