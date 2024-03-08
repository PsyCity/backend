from django.utils import timezone

from rest_framework import status, exceptions, mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action

from core.models import Team

from team_api.serializers import TeamMoneySerializer, TeamPropertySerializer, TeamMoneySerializerwtb
from team_api.utils import game_state, response


class TeamMoneyViewSetwtb(GenericViewSet):

    queryset = Team.objects.all()
    
    serializer_class = TeamMoneySerializerwtb


    @game_state(["Day"])
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)   
            serializer.is_valid(raise_exception=True)
            self.perform_exchange(serializer)
            return Response(
                data={
                    "message":"Money transferred successfully.",
                    "data": [],
                    "result" : None
                },
                status=status.HTTP_200_OK
            )
        except Team.DoesNotExist :
            return Response(
                data={
                    "message": "Team Not found.",
                    "data" : [],
                    "result" : None
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except exceptions.ValidationError as e:
            return Response(
                data={
                 "message": "Validation Error.",
                 "data": [e.detail],
                 "result": None
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        
        except Exception as e:
            return Response(
                data={
                    "message": "Something went wrong.",
                    "data": [e.__str__()],
                    "result": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )


    def perform_exchange(self, serializer):
        team: Team = serializer.validated_data.get("team")
        amount = serializer.validated_data.get("amount")
        team.bank += amount 
        team.wallet -= amount
        team.last_bank_action = timezone.now()
        team.save()



class TeamMoneyViewSet(
    GenericViewSet
    ):
    
    queryset = Team.objects.all()
    
    serializer_class = TeamMoneySerializer


    @game_state(["Day"])
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)   
            serializer.is_valid(raise_exception=True)
            self.perform_exchange(serializer)
            return Response(
                data={
                    "message":"Money transferred successfully.",
                    "data": [],
                    "result" : None
                },
                status=status.HTTP_200_OK
            )
        except Team.DoesNotExist :
            return Response(
                data={
                    "message": "Team Not found.",
                    "data" : [],
                    "result" : None
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except exceptions.ValidationError as e:
            return Response(
                data={
                 "message": "Validation Error.",
                 "data": [e.detail],
                 "result": None
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        
        except Exception as e:
            return Response(
                data={
                    "message": "Something went wrong.",
                    "data": [e.__str__()],
                    "result": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )


    def perform_exchange(self, serializer):
        team: Team = serializer.validated_data.get("team")
        amount = serializer.validated_data.get("amount")
        team.bank -= amount 
        team.wallet += amount
        team.last_bank_action = timezone.now()
        team.save()



class PropertyViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin
):
    queryset = Team.objects.filter(state="Active").all().select_related()
    serializer_class = TeamPropertySerializer

    @response
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    