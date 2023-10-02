from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .serializers import DiscordPlayer
from rest_framework import status
from core.models import (
    Player
)

from . import schema
# Create your views here.


class PlayerIdByDiscord(GenericAPIView):
    serializer_class = DiscordPlayer
    def get_queryset(self):
        discord = self.request.data.get("discord")
        return Player.objects.filter(discord_username=discord).first()

    def post(self, request, *args, **kwargs):
        player = self.get_queryset()
        if player:
            return Response({"id":player.pk})
        return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)