from django.utils import timezone

from rest_framework.viewsets import (
    GenericViewSet,
    mixins
)
from rest_framework.response import Response
from rest_framework import status

from core.models import Team
from team_api.serializers import LoanSerializer, LoanRepaySerializer
from team_api.utils import response, game_state

class Receive(
    GenericViewSet,
    ):

    serializer_class = LoanSerializer

    @response
    @game_state(["Day"])
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            data={
                "message":"Loan request accepted.",
                "data": [],
                "result": None
            },
            status=status.HTTP_200_OK
        )
    
    def perform_create(self, serializer):
        team: Team = serializer.validated_data["team"]
        team.last_bank_action = timezone.now()
        team.bank_liabilities += serializer.validated_data["amount"]
        team.wallet += serializer.validated_data["amount"]
        team.save()


class Repay(GenericViewSet):
    serializer_class = LoanRepaySerializer

    @response
    @game_state(["Day"])
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            data={
                "message":"Payed successfully.",
                "data": [],
                "result": None
            },
            status=status.HTTP_200_OK
        )        
    
    def perform_create(self, serializer):
        team :Team = serializer.validated_data["team"]
        team.last_bank_action = timezone.now()
        team.bank_liabilities -= serializer.validated_data["amount"]
        team.wallet -= serializer.validated_data["amount"] 
        team.save()