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
    EscapeRoomAfterPuzzleSerializer,
    EscapeRoomListSerializer,
    EscapeRoomReserve,
    BankRobberyWaySerializer,
    BankRobberyListSerializer,
    BankRobberyOpenSerializer,
    BankRobberyOpenDepositBoxSerializer,
    BankSensorInstallWaySerializer,
    serializers
)

from core.models import (
    Player,
    ConstantConfig, 
    Contract,
    BankDepositBox,
    EscapeRoom,
    BankRobbery,
    TeamFeature,
    Team
)

from team_api.utils import transfer_money, response, ListModelMixin, find_boxes
from team_api.schema import deposit_list_schema, bank_robbery_list_schema

import random
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
    - [x] after puzzle
    - [ ] report
    - [ ] exception handlers
    - [ ] define discord api
    """

    queryset = EscapeRoom.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return EscapeRoomListSerializer
        elif self.action == "reserve_to_solve":
            return EscapeRoomReserve 
        elif self.action == "after_puzzle":
            return EscapeRoomAfterPuzzleSerializer 
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
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        d = self.perform_update_solve(serializer)
        return Response(
            data={
                "message": "ok",
                "data": d,
                "result":None
            },
            status=status.HTTP_200_OK
        )

    def perform_update_solve(self, serializer):
        instance = serializer.instance
        data = []
        if serializer.validated_data["solved"]:
            instance.state = 3
            data = [{"box_id": instance.bank_deposit_box.id}]
        else:
            instance.state = 4

        instance.save()
        return data



    @action(["post"], True)
    def report(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update_report(serializer)
        return Response(
            data={
                "message":"Reported successfully.",
                "data": [],
                "result": None
            },
            status=status.HTTP_200_OK
        )

    def perform_update_report(self, serializer):
        room :EscapeRoom = serializer.instance
        police = room.solver_police
        mafia = room.bank_deposit_box.rubbery_team
        amount = room.bank_deposit_box.money
        conf = ConstantConfig.objects.last()
        mafia_amount = amount * conf.penalty_percent // 100
        police_amount = amount * conf.bonus_percent // 100
        if mafia.wallet < mafia_amount:
            mafia_amount -= mafia.wallet
            mafia.bank_liabilities += mafia_amount
            mafia.wallet = 0
            mafia.save()
        else:
            mafia.wallet -= mafia_amount
        police.wallet += police_amount
        police.save()

class BankRobberyWayViewSet(
    GenericViewSet,
    mixins.CreateModelMixin
    ):

    serializer_class = BankRobberyWaySerializer


    @response
    def create(self, request, *args, **kwargs):
        r = super().create(request, *args, **kwargs)
        #NOTICE: Need to choose a Escape Room??
        return Response(
            data={
                "message": "robbery approved.",
                "data": [],
                "result": r.data.get("id")
            },
            status=status.HTTP_200_OK
        )
    
    def perform_create(self, serializer):
        citizen = serializer.validated_data.get("contract").second_party_team

        instance = serializer.save(
            citizen=citizen
        )
        self.consider_escape_room(instance)
        self.add_to_mafia_efforts(serializer.validated_data["mafia"])
        self.archive_contract(serializer)

    def archive_contract(self, serializer):
        try:
            contract :Contract  = serializer.validated_data["contract"]
            contract.archive = True
            contract.save()
        except:
            #LOG
            raise exceptions.APIException("Failed to archive contract.")

    def consider_escape_room(self, instance:BankRobbery):
        #TODO : Do not use random :(
        escape_rooms = EscapeRoom.objects.filter(state=0).all()

        if not escape_rooms:
            raise exceptions.APIException("Lack off escape room.")
            
        room = random.choice(escape_rooms)
        instance.escape_room = room        
        room.no_valid_mafia -= 1
        room.state = 5
        room.save()
        instance.save()
 
    def add_to_mafia_efforts(self, mafia):
        
        profile = mafia.team_feature.first()
        
            
        profile.mafia_reserved_escape_room += 1
        profile.save()


class BankRobberyViewSet(
    GenericViewSet,
    ListModelMixin    
    ):

    queryset = BankRobbery.objects.all()
    serializer_class = BankRobberyListSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BankRobberyListSerializer
        elif self.action == "open_escape_room":
            return BankRobberyOpenSerializer
        elif self.action == "open_deposit_box":
            return BankRobberyOpenDepositBoxSerializer
        return serializers.Serializer

        

    @bank_robbery_list_schema
    @response
    def list(self, request, *args, **kwargs):
        owner = request.GET["team_id"]
        if not owner:
            raise exceptions.ValidationError("Set team_id in url params.")

        self.validate_owner(owner)
        queryset = self.queryset.filter(
            mafia=owner
        ).all()
        serializers = self.get_serializer(queryset, many=True)
        return Response(
            data={
                "message": "Team Bank Robberies",
                "data": serializers.data,
                "result": None
            }
        )


    def validate_owner(self, owner_pk):
        try:
            team = Team.objects.get(pk=owner_pk)
        except:
            raise exceptions.NotFound("team not found")
        
        if team.team_role != "Mafia":
            raise exceptions.NotAcceptable("Not mafia.")

    @action(
            methods=["patch"],
            detail=True
            )
    @response
    def open_escape_room(self, request, *args, **kwargs):
        instance: BankRobbery = self.get_object()
        
        serializer = self.get_serializer(instance,
                                         data=request.data,
                                         partial=True
                                         )
        
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            data={
                "message": "good luck.",
                "data": [],
                "result":None
            }
        )
    
    def perform_update(self, serializer):
        serializer.save(
            state=2,
            opening_time=timezone.now()
        )

    @action(
        methods=["POST"],
        detail=True,
        url_path="deposit_box"
    )
    @response
    def open_deposit_box(self, request, bpk=None, *args, **kwargs):
        instance: BankRobbery = self.get_object()
        
        serializer = self.get_serializer(
            instance,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.is_acceptable()
        self.perform_open_box(serializer)
        return Response(
            data={
                "message": "Box Opened successfully.",
                "data" : [],
                "result": None
            }
        )


    def perform_open_box(self, serializer):
        box = serializer.validated_data["deposit_box"]
        #box is selected box
        boxes = find_boxes(box)
        boxes = self.perform_on_boxes(serializer, boxes)
        box = self.select_box(boxes, box)
        #box is a random box. kind of random
        self.attach_box_and_room(box, serializer.instance.escape_room)
        self.transfer_money(serializer, box)
        self.sensor_report(boxes)


    def perform_on_boxes(self, serializer, boxes):
        """do any perform on all boxes together"""
        mafia :Team = serializer.instance.mafia

        for b in boxes:
            b.robbery_state = True
            b.rubbery_team = mafia
            b.save()
        return boxes

    def select_box(self, boxes, box):
        """
        select a box with no sensor if available 
        """
        sensor_not_installed = list(filter(lambda b: not b.sensor_state, boxes))
        if sensor_not_installed:
            box = random.choices(sensor_not_installed)[0]
        return box


    def sensor_report(self, boxes):
        """NOTICE : this one needs API from Client side"""
        ...


    def attach_box_and_room(self,
                            box:BankDepositBox,
                            room:EscapeRoom
                            ): 
        room.bank_deposit_box = box
        room.state = 1
        room.save()


    def transfer_money(self, serializer, box):
        """
        transfer money to citizen and pay the contract
        """

        robbery: BankRobbery = serializer.instance
        citizen :Team = robbery.citizen
        contract:Contract = robbery.contract
        mafia: Team = robbery.mafia

        citizen.wallet += box.money
        robbery.robbery_amount = box.money
        box.money = 0
        mafia.wallet += contract.cost
        contract.state = 3
        contract.archive = True

        robbery.save()
        citizen.save()
        contract.save()
        box.save()
        mafia.save()



class BankSensorInstallWay(
    GenericViewSet,
    mixins.CreateModelMixin
):
    serializer_class = BankSensorInstallWaySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.is_acceptable()
        room = self.choose_room()
        self.perform_create(serializer, room)

        return Response(
            data={
                "message":"",
                "data": [],
                "result": serializer.instance.pk
            },
            status=status.HTTP_201_CREATED
            )

    def choose_room(self) -> EscapeRoom :
        escape_rooms = EscapeRoom.objects.filter(state=0).all()

        if not escape_rooms:
            raise exceptions.APIException("Lack off escape room.")

        #filter rooms to make sure 
        #check no_valid_citizen
        room = random.choice(escape_rooms)
        room.no_valid_citizen -= 1
        room.save()
        return room
    
    def perform_create(self, serializer, room):
        self.perform_on_team(serializer)
        serializer.save(room=room)


    def perform_on_team(self,
                        serializer: BankSensorInstallWaySerializer
                        ):
        team : Team = serializer.validated_data["team"]
        profile = team.team_feature.first()
        profile.citizen_opened_night_escape_rooms += 1
        profile.save()
