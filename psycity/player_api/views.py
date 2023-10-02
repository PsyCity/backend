from django.db import transaction
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework import status
from core.models import TeamJoinRequest
from core.models import Player
from player_api.serializers import PlayerSerializer, DiscordPlayer, LoanReceiveSerializer
from . import schema
class PlayerLeftTeam(UpdateAPIView):
    http_method_names = ["patch"]
    
    def get_serializer_class(self):
        return PlayerSerializer
    @schema.left_team_schema
    def patch(self, request, *args, **kwargs):
        try:
            player = Player.objects.get(pk=request.data["player_id"])
        except Player.DoesNotExist:
            return Response({
                "message": "player doesn't exist",
                "data": [],
                "result": None,
            }, status=status.HTTP_404_NOT_FOUND)
        if player.team is not None:
            player.team = None
            player.status = Player.STATUS_CHOICES[1][0]
            player.save()
            return Response({
                "message": "player team removed",
                "data": [],
                "result": None,
            }, status=status.HTTP_200_OK) 
        else:
            return Response({
                "message": "player doesn't have any team",
                "data": [],
                "result": None,
            }, status=status.HTTP_400_BAD_REQUEST)   

class PlayerJoinTeam(UpdateAPIView):
    http_method_names = ["patch"]
    
    def get_serializer_class(self):
        return PlayerSerializer

    @transaction.atomic
    def patch(self, request):
        try:
            found_request = TeamJoinRequest.objects.get(pk=request.data["request_id"])
            if (found_request.state == "inactive"):
                return Response({
                    "message": "team join request is already inactive",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)
            found_request.player.team = found_request.team
            found_request.team.wallet = found_request.player.wallet
            found_request.player.wallet = 0
            found_request.team.bank_liabilities = found_request.player.bank_liabilities
            found_request.player.bank_liabilities = 0
            found_request.team.save()
            found_request.player.save()
            TeamJoinRequest.objects.filter(player=found_request.player).update(state="inactive")
            return Response({
                "message": "player joined the team",
                "data": [],
                "result": None,
            }, status=status.HTTP_200_OK)
        except TeamJoinRequest.DoesNotExist:
            return Response({
                "message": "team join request doesn't exist",
                "data": [],
                "result": None,
            }, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({
                "message": "something went wrong",
                "data": [],
                "result": None,
            }, status=status.HTTP_400_BAD_REQUEST)

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


class LoanReceive(mixins.CreateModelMixin,
                 GenericViewSet):
    serializer_class = LoanReceiveSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.perform_create(serializer)

    def perform_create(self, serializer:LoanReceiveSerializer):

        try:
            player = Player.objects.get(
                pk=serializer.validated_data.get("player_id")
            )
        except:
            return Response(
                data={
                "message": "player not found.",
                "data": [],
                "result": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        if player.status != Player.STATUS_CHOICES[1][0]:
            return Response(
                data={
                "message": "Player is not homeless",
                "data": [],
                "result": None,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        

        amount = serializer.validated_data.get("amount")
        player.wallet += amount
        player.bank_liabilities += amount
        player.save()
        return Response(
            data={
                "message": "Loan amount added to player's wallet.",
                "data": [],
                "result": None,
                },
        )