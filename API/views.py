from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from rest_framework.decorators import api_view
from rest_framework.response import Response

from Members.models import Player
from .serializers import PlayerSerializer


@api_view(["GET"])
def player_list(request):
    if request.method == "GET":
        objects = Player.objects.all()
        serializer = PlayerSerializer(objects, many=True)
        return Response(serializer.data)
