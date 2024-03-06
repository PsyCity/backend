from rest_framework.viewsets import (
    GenericViewSet, 
    mixins,
    generics,
)
from django.db.models import Q
from team_api.utils import response, game_state

from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions

from core.models import Contract, Question, Team, Player, Report
from core.config import HIDDEN_ID_LEN
from team_api.serializers import(
    ContractRegisterSerializer,
    ContractApprovementSerializer,
    ContractPaySerializer,
    ContractRejectSerializer,
    TeamContractListSerializer,
)


class Register(
    GenericViewSet,
    mixins.CreateModelMixin
    ):

    serializer_class = ContractRegisterSerializer
    team_query_set = Team.objects.all()

    @response
    @game_state()
    def create(self, request, *args, **kwargs):
        if request.data.get('first_party_team'):
            if len(str(request.data.get('first_party_team'))) == HIDDEN_ID_LEN:
                team = self.team_query_set.filter(hidden_id=request.data.get('first_party_team'))
                if not team:
                    return Response(
                        data={
                        "message": "first_party_team yaft nashod.",
                        "data": [],
                        "result": None,
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
                request.data['first_party_team'] = team.first().channel_role

        if request.data.get('second_party_team'):
            if len(str(request.data.get('second_party_team'))) == HIDDEN_ID_LEN:
                team = self.team_query_set.filter(hidden_id=request.data.get('second_party_team'))
                if not team:
                    return Response(
                        data={
                        "message": "second_party_team yaft nashod.",
                        "data": [],
                        "result": None,
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
                request.data['second_party_team'] = team.first().channel_role

        if request.data.get('first_party_team', 'f') == request.data.get('second_party_team', 's'):
            return Response(
                        data={
                        "message": "team ha bayad motefavet bashand.",
                        "data": [],
                        "result": None,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        r = super().create(request, *args, **kwargs)
        return Response(
            data={
                "message": "gharardad ba movafaghiat sabt shod.",
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
    team_query_set = Team.objects.all()

    @response
    @game_state()
    def partial_update(self, request, *args, **kwargs):
        if request.data.get('team'):
            if len(str(request.data.get('team'))) == HIDDEN_ID_LEN:
                team = self.team_query_set.filter(hidden_id=request.data.get('team'))
                if not team:
                    return Response(
                        data={
                        "message": "team yaft nashod.",
                        "data": [],
                        "result": None,
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
                request.data['team'] = team.first().channel_role
        super().partial_update(request, *args, **kwargs)
        return Response(
            data={
                "message": "bamovafaghiat emza shod.",
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
    @game_state()
    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response(
            data={
                "message": "ba movafaghiat pardakht shod.",
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
                f"shekast dar enteghl poll bain {contract.first_party_team} va {contract.second_party_team}."
                )
        
class Reject(generics.UpdateAPIView):
    http_method_names = ["patch"]
    
    def get_serializer_class(self):
        return ContractRejectSerializer

    @game_state()
    def patch(self, request):
        try:
            contract = Contract.objects.get(pk=request.data["contract_id"])
            if (contract.state != 2 or contract.archive == True):
                return Response({
                    "message": f"vaziat eshtebah dar gharardad. vaziat feli: {contract.state} and archive is {contract.archive}",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)
            team = request.data.get('team_id', None)
            player = request.data.get('player_id', None)
            if not player and not team:
                return Response({
                    "message": "player ya team lazem ast",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)
            if team:
                team_obj = Team.objects.get(Q(hidden_id=team) | Q(channel_role=team))
                if team_obj not in [contract.first_party_team, contract.second_party_team]:
                    return Response({
                        "message": "gharardad motealegh be in team nist",
                        "data": [],
                        "result": None,
                    }, status=status.HTTP_400_BAD_REQUEST)


            else:
                player_obj = Player.objects.get(pk=player)
                if player_obj not in [contract.first_party_player, contract.second_party_player]:
                    return Response({
                        "message": "gharardad motealegh be in player nist",
                        "data": [],
                        "result": None,
                    }, status=status.HTTP_400_BAD_REQUEST)

            # archive and reject the contract
            contract.state = 3
            contract.is_rejected = True
            contract.archive = True
            report = Report.objects.create(
                description="contract rejection.",
                report_type=2,
                contract=contract
            )
            if team:
                report.team_reporter = team
            else:
                report.player_reporter = player_obj
            report.save()
            contract.save()

            return Response({
                "message": "gharardad ba movafaghiat rad shod.",
                "data": [],
                "result": None,
            }, status=status.HTTP_200_OK)
        except Contract.DoesNotExist:
            return Response({
                "message": "gharardad vojod nadarad",
                "data": [],
                "result": None,
            }, status=status.HTTP_404_NOT_FOUND)
        except Team.DoesNotExist:
            return Response({
                "message": "team vojad nadarad",
                "data": [],
                "result": None,
            }, status=status.HTTP_404_NOT_FOUND)
        except Player.DoesNotExist:
            return Response({
                "message": "player vojod nadarad",
                "data": [],
                "result": None,
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            raise e
            return Response({
                "message": "khata: ye chisi eshtebah shode",
                "data": [],
                "result": None,
            }, status=status.HTTP_400_BAD_REQUEST)
    
        
class TeamContracts(generics.GenericAPIView):
    def get(self, request, team_id, *args, **kwargs):
        contracts = Contract.objects.filter(first_party_team=team_id, state=2) | Contract.objects.filter(second_party_team=team_id)
        contracts = list(filter(lambda contract: contract.state in [1, 2], contracts))
        serializer = TeamContractListSerializer(contracts, many=True)
        return Response(serializer.data)