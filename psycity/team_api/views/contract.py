from rest_framework.viewsets import (
    GenericViewSet, 
    mixins,
    generics,
)

from team_api.utils import response

from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions

from core.models import Contract, Question, Team
from team_api.serializers import(
    ContractRegisterSerializer,
    ContractApprovementSerializer,
    ContractPaySerializer,
    TeamContractListSerializer,
)


class Register(
    GenericViewSet,
    mixins.CreateModelMixin
    ):

    serializer_class = ContractRegisterSerializer
    team_query_set = Team.objects.all()

    @response
    def create(self, request, *args, **kwargs):
        if request.data.get('first_party_team'):
            if len(str(request.data.get('first_party_team'))) == 12:
                team = self.team_query_set.filter(hidden_id=request.data.get('first_party_team'))
                if not team:
                    return Response(
                        data={
                        "message": "first_party_team not found.",
                        "data": [],
                        "result": None,
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
                request.data['first_party_team'] = team.first().channel_role

        if request.data.get('second_party_team'):
            if len(str(request.data.get('second_party_team'))) == 12:
                team = self.team_query_set.filter(hidden_id=request.data.get('second_party_team'))
                if not team:
                    return Response(
                        data={
                        "message": "second_party_team not found.",
                        "data": [],
                        "result": None,
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
                request.data['second_party_team'] = team.first().channel_role
        r = super().create(request, *args, **kwargs)
        return Response(
            data={
                "message": "Contract created successfully.",
                "data": [],
                "result": r.data.get("id")
            },
            status=status.HTTP_201_CREATED
        )
        
    def perform_create(self, serializer):
        serializer.save(
            first_party_agree=True,
            second_party_agree=False,
            archive=False,
            state=1
        )
    
class Approvement(
    GenericViewSet,
    mixins.UpdateModelMixin
    ):
    http_method_names = ["patch"]

    serializer_class = ContractApprovementSerializer
    
    queryset = Contract.objects.filter(
        first_party_agree=True, 
        second_party_agree=False,
        state=1
        )

    @response
    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response(
            data={
                "message": "signed successfully.",
                "data": [],
                "result": None
            },
            status=status.HTTP_200_OK
        )
            
    def perform_update(self, serializer):
        serializer.save(
            second_party_agree=True,
            state=2
        )
        
class Pay(
    GenericViewSet,
    mixins.UpdateModelMixin
    ):

    serializer_class = ContractPaySerializer
    queryset = Contract.objects.filter(
        state=2,
        first_party_agree=True,
        second_party_agree=True,
        archive=False
    )
    http_method_names = ["patch"]

    @response
    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response(
            data={
                "message": "Payed successfully.",
                "data":[],
                "result": None
            },
            status=status.HTTP_200_OK
        )

    def perform_update(self, serializer):
        contract = serializer.instance
        self.pay(contract)

        serializer.save(
            state=3,
            archive=True,
        )
    
    def pay(self, contract:Contract):
        try:
            if contract.contract_type == 'question_ownership_transfer':
                contract.question.last_owner = contract.second_party_team
                contract.question.save()
            elif contract.contract_type == 'homeless_solve_question':
                # todo:
                ...
            contract.first_party_team.wallet -= contract.cost
            contract.first_party_team.save()
            contract.second_party_team.wallet += contract.cost
            contract.second_party_team.save()
        except:
            raise exceptions.APIException(
                f"failed to transfer money between {contract.first_party_team} and {contract.second_party_team}."
                )
        
class TeamContracts(generics.GenericAPIView):
    def get(self, request, team_id, *args, **kwargs):
        contracts = Contract.objects.filter(first_party_team=team_id) | Contract.objects.filter(second_party_team=team_id)
        serializer = TeamContractListSerializer(contracts, many=True)
        return Response(serializer.data)