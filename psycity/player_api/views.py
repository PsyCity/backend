from django.db import transaction
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework import status
from rest_framework import exceptions
from core.models import TeamJoinRequest
from core.models import Player, Contract
from rest_framework.serializers import Serializer
from player_api.serializers import (
    PlayerSerializer,
    DiscordPlayer,
    LoanRepaymentSerializer,
    LoanReceiveSerializer,
    BodyguardSerializer
)
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
    @schema.join_team_schema
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
            found_request.team.bank_liabilities += found_request.player.bank_liabilities
            found_request.player.bank_liabilities = 0
            found_request.player.status = "TeamMember"
            # FIXME : Need to remove player role ??
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


class LoanReceive(GenericAPIView):
    serializer_class = LoanReceiveSerializer

    def post(self, request, *args, **kwargs):
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


class BodyguardViewSet(GenericViewSet, 
                       mixins.UpdateModelMixin,
                       mixins.CreateModelMixin,):

    queryset = Contract.objects.all()
    def get_serializer_class(self):
        if self.action =="create":
            return BodyguardSerializer
        return Serializer


    #schema => description
    def create(self, request, *args, **kwargs):    
        try:

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            contract = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                data={
                    "message": "Contract object created successfully",
                    "data" : [],
                    "result" : contract.pk
                },
                status=status.HTTP_201_CREATED,
                headers=headers)

        except exceptions.ValidationError as e:
            return self.responser(
                message="Not a valid request",
                data=[e.detail[er][0] for er in e.detail],
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except exceptions.NotAcceptable as e:
            return self.responser(
                message="Request is not Acceptable",
                data=[e.detail],
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        except Exception as e:
            return self.responser(
                message="Something went wrong",
                status=status.HTTP_400_BAD_REQUEST
            )
        
    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        return serializer.save(
            state=1,
            contract_type="bodyguard_for_the_homeless",
            terms = f"An offer for protecting a homeless player({validated_data.get('second_party_player').__str__()}) for {validated_data['cost']} amount of money from {validated_data.get('first_party_team').__str__()}",
            first_party_agree = True,
            second_party_agree = False,
            archive = False
            )
    def partial_update(self, request, *args, **kwargs):
        try:
            kwargs['partial'] = True
            return self.update(request, *args, **kwargs)
        
        except Exception as e:
            return self.responser(
                "Something went wrong",
                data=e.__str__()
            )


    def update(self, request, *args, **kwargs):  
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        self.perform_update(instance)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return self.responser()
        
    def perform_update(self, instance):
        instance.state = 2
        instance.second_party_agree = True
        instance.save()


    def responser(self,
                  message:str="OK",
                  data:list=[],
                  result=None,
                  status=status.HTTP_200_OK
                  ):
        return Response(
            data={
                "message": message,
                "data":data,
                "result" : result
            },
            status= status
        )
