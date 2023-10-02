from rest_framework import serializers
from core.models import Player

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = []
class DiscordPlayer(serializers.Serializer):
    discord = serializers.CharField()
