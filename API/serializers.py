from rest_framework import serializers

from Members.models import Player, Team


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ("id", "first_name", "last_name", "phoneNumber", "email")
        read_only_fields = ("id",)


class SubstituteSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)

    class Meta:
        model = Player
        fields = ("id", "first_name", "last_name", "username")
        read_only_fields = ("id",)

    def create(self, validated_data):
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        username = f"{first_name}.{last_name}"
        if Player.objects.filter(username=username).exists():
            count = str(Player.objects.filter(username__startswith=username).count() + 1)
            username = f"{first_name}.{last_name}{count}"
        validated_data['username'] = username
        return super().create(validated_data)


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("id", "name", "players")
        read_only_fields = ("id",)

    
    
