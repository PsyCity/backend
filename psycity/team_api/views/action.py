from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.decorators import action
from rest_framework import status
from rest_framework import exceptions

from team_api.serializers import (
    KillHomelessSerializer, 
    DepositBoxSensorReportListSerializer, 
    EscapeRoomListSerializer,
    EscapeRoomReserve,
    serializers
)

from core.models import (
    Player,
    ConstantConfig, 
    Contract,
    BankDepositBox,
    EscapeRoom
)

from team_api.utils import transfer_money
from team_api.schema import deposit_list_schema


class KillHomelessViewSet(GenericViewSet):

    serializer_class = KillHomelessSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data, code = self.perform_kill(serializer)
            return Response(
                data=data,
                status=code
            )
        except Player.DoesNotExist as e:
            return Response(
                data={
                    "message" : "cant find the player",
                    "data" : [],
                    "result" : None
                    },
                    status=status.HTTP_404_NOT_FOUND
            )
        except exceptions.NotAcceptable as e:
            return Response(
                data={
                    "message": e.detail,
                    "data": [],
                    "result" : None
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        except Exception as e:
            return Response(
                data={
                    "message": "something went wrong.",
                    "data" : [],
                    "result": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_kill(self, serializer):
        team = serializer.validated_data.get("team_id")
        player = serializer.validated_data.get("homeless_id")
        player.last_assassination_attempt = timezone.now()
        conf = get_object_or_404(ConstantConfig.objects.filter())
        
        bodyguard, contract = self.bodyguard_exist(player)
        if bodyguard:
            if team.level < bodyguard.level:
                """
                decrease contract_amount + penaly_percent from police
                add contract_amount + bonus to bodyguard 
                kill homeless
                """
                transfer_money(
                    amount=contract.cost,
                    from_team=bodyguard,
                    penalty_percent=conf.penalty_percent,
                    to_team=team,
                    bonus_percent=conf.bonus_percent
                )

                self.kill(player)
                data = {
                    "message" : f"Mafia Wins. {player.__str__()} is dead.",
                    "data" : [],
                    "result" : 1
                }
                
            elif team.level == bodyguard.level:

                transfer_money(
                    amount=contract.cost // 2,
                    from_team=bodyguard,
                    to_team=team,
                    penalty_percent=0,
                    bonus_percent=0
                )
                data = {
                    "message" : "homeless saved. bodyguard level == mafia level",
                    "data": [],
                    "result" : 2
                }
                
            elif team.level > bodyguard.level:
                """
                transfer from mafia to bodyguard 
                """
                transfer_money(
                    amount=contract.cost,
                    from_team=team,
                    to_team=bodyguard,
                    bonus_percent=conf.bonus_percent,
                    penalty_percent=conf.penalty_percent
                )
                data={
                    "message": "Bodyguard wins. mafia level < police level.",
                    "data": [],
                    "result":3
                }

            contract.archive = True
            contract.save()

            return data, status.HTTP_200_OK
        
        self.kill(player)
        data={
            "message": "homeless killed successfully.",
            "data" :[],
            "result" : 0
        } 

        return data, status.HTTP_200_OK
    
    def kill(self, player):
        print(f"[KILL] killing {player.__str__()}")
        player.player_role.clear()
        player.status = "Dead"
        player.save()

    def bodyguard_exist(self, player):
        contract = Contract.objects.filter(
            state=2,
            contract_type="bodyguard_for_the_homeless",
            second_party_player=player,
            first_party_agree=True,
            second_party_agree=True,
            archive=False
        ).last()
        if contract:
            return player.bodyguard_team, contract
        return False, None
    
class DepositBoxSensor(GenericViewSet):

    queryset = BankDepositBox.objects.all() 
    http_method_names=["get", "patch", "options"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return DepositBoxSensorReportListSerializer
        return serializers.Serializer

    @deposit_list_schema
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            owner = request.GET.get("sensor_owner_pk")
            if not owner:
                raise exceptions.ValidationError("set sensor_owner_pk in api params")

            queryset = self.queryset.filter(sensor_owner=owner, reported=False).all()
        except exceptions.ValidationError as e:
            return Response(
                data={
                    "message": "something went wrong.",
                    "data": e.detail,
                    "result": None
                }
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
    
    
    
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.reported:
                raise exceptions.NotAcceptable("Already reported.")
            self.perform_update(instance)

            return Response(
                data={
                    "message": "Rubbery reported successfully.",
                    "data": [],
                    "result": None
                },
                status=status.HTTP_200_OK
            )
        except BankDepositBox.DoesNotExist:
            return Response(
                data={
                    "message": "Box not found.",
                    "data":[],
                    "result":None
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except ConstantConfig.DoesNotExist:
            return Response(
                data={
                    "message": "Config not found.",
                    "data":[],
                    "result":None
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except exceptions.NotAcceptable as e:
            return Response(
                data={
                    "message": "Request is not acceptable.",
                    "data": [e.detail],
                    "result": None
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        
        except Exception as e:
            return Response(
                data={
                    "message": "Something went wrong",
                    "data": [],
                    "result": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_update(self, box):
        conf = ConstantConfig.objects.get()
        team = box.sensor_owner
        team.wallet += (box.money) * conf.bonus_percent // 100
        box.reported = True
        team.save()
        box.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)



class DiscoverBankRobber(
    GenericViewSet,
    mixins.ListModelMixin
    ):
    """
    TODO: 
    - [x] List EscapeRooms
    - [x] reserve to solve
    - [ ] after puzzle
    - [ ] report
    - [ ] exception handlers
    - [ ] define discord api
    """

    queryset = EscapeRoom.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return EscapeRoomListSerializer
        elif self.action == "reserve_escape_room":
            return EscapeRoomReserve 
        return serializers.Serializer
    
    @action(["post"], True)
    def reserve_to_solve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update_reserve(serializer)
        return Response(
            data={
                "message": "reserved",
                "data": [],
                "result": None
            },
            status=status.HTTP_200_OK
        )
    
    def perform_update_reserve(self, serializer):
        instance = serializer.instance
        instance.state = 2
        instance.solver_police = serializer.validated_data.get("team_id")
        instance.no_valid_police -= 1
        instance.save()

    @action(["post"], True)
    def after_puzzle(self, request, *args, **kwargs):
        ...

    @action(["post"], True)
    def report(self, request, *args, **kwargs):
        ...