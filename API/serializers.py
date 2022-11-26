from rest_framework import serializers

from Members.models import Player, Team


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ("id", "first_name", "last_name", "phoneNumber", "email")
