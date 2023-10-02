from django.db import transaction
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView
from rest_framework.generics import GenericAPIView
from rest_framework import status
from core.models import TeamJoinRequest
from core.models import Player
from player_api.serializers import PlayerSerializer, DiscordPlayer, LoanRepaymentSerializer
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

class PlayerLoanRepayment(GenericAPIView):
    serializer_class = LoanRepaymentSerializer

    def post(self, request, *args, **kwargs):
        try:
            player = Player.objects.get(pk=request.data['player_id'])
            repayment_amount = request.data['amount']

            liabilities = player.bank_liabilities
            wallet = player.wallet

            if player.status != 'Homeless':
                return Response({
                    "message": "only homeless can repayment his/her loan",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)
            if repayment_amount <= 0:
                return Response({
                    "message": "amount must be positive",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)
            
            
            if repayment_amount > wallet:
                return Response({
                    "message": "amount is bigger than player wallet value",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)

            if liabilities <= 0:
                return Response({
                    "message": "player liability is 0",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)
            
            amount_to_reduce = min(liabilities, repayment_amount)

            player.wallet -= amount_to_reduce
            player.bank_liabilities -= amount_to_reduce
            player.save()

            return Response({
                "message": "loan repayment successful. %i repaymented" % amount_to_reduce,
                "data": [],
                "result": None,
            }, status=status.HTTP_200_OK)
        except Player.DoesNotExist:
            return Response({
                "message": "player not found",
                "data": [],
                "result": None,
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "message": "something went wrong",
                "data": [],
                "result": None,
            }, status=status.HTTP_400_BAD_REQUEST)