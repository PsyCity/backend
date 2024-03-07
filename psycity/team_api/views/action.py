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
    BankSensorInstallationOpenSerializer,
    BankRobberyOpenDepositBoxSerializer,
    BankSensorInstallWaySerializer,
    BankSensorInstallationListSerializer,
    BankSensorInstallOpenDepositBox,
    DepositBoxHackSerializer,
    DepositBoxRobberySerializer,
    DepositBoxHackCheckSerializer,
    FindCardSerializer,
    serializers,
)

from core.models import (
    Player,
    ConstantConfig,
    Contract,
    BankDepositBox,
    EscapeRoom,
    BankRobbery,
    WarehouseBox,
    TeamQuestionRel,
    TeamFeature,
    BankSensorInstall,
    Team,
    MoneyChangeLogger,
)
from abc import ABC, abstractmethod
from team_api.utils import (
    ListModelMixin,
    transfer_money,
    response,
    game_state,
    find_boxes,
    )

from team_api.views.base_actions import BankPenetrationBaseViewSet
from team_api.schema import deposit_list_schema, bank_robbery_list_schema

import random


class KillHomelessViewSet(GenericViewSet):
    serializer_class = KillHomelessSerializer

    @game_state(["Night"])
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
                    bonus_percent=conf.bonus_percent,
                )

                self.kill(player)
                data = {
                    "message": f"Mafia Wins. {player.__str__()} is dead.",
                    "data": [],
                    "result": 1,
                }

            elif team.level == bodyguard.level:
                transfer_money(
                    amount=contract.cost // 2,
                    from_team=bodyguard,
                    to_team=team,
                    penalty_percent=0,
                    bonus_percent=0,
                )
                data = {
                    "message": "homeless saved. bodyguard level == mafia level",
                    "data": [],
                    "result": 2,
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
                    penalty_percent=conf.penalty_percent,
                )
                data = {
                    "message": "Bodyguard wins. mafia level < police level.",
                    "data": [],
                    "result": 3,
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
            archive=False,
        ).last()
        if contract:
            return player.bodyguard_team, contract
        return False, None


class DepositBoxSensor(GenericViewSet):
    queryset = BankDepositBox.objects.all()
    http_method_names = ["get", "patch", "options"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return DepositBoxSensorReportListSerializer
        return serializers.Serializer

    @deposit_list_schema
    @game_state(["Night"])
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
                    "result": None,
                }
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @game_state("Night")
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.reported:
                raise exceptions.NotAcceptable("gozaresh shodeh.")
            self.perform_update(instance)

            return Response(
                data={
                    "message": "Rubbery reported successfully.",
                    "data": [],
                    "result": None,
                },
                status=status.HTTP_200_OK,
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
                    "result": None,
                },
                status=status.HTTP_406_NOT_ACCEPTABLE,
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
        room: EscapeRoom = serializer.instance
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
        # NOTICE: Need to choose a Escape Room??
        return Response(
            data={
                "message": "robbery approved.",
                "data": [],
                "result": r.data.get("id"),
            },
            status=status.HTTP_200_OK,
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
            contract: Contract = serializer.validated_data["contract"]
            contract.archive = True
            contract.save()
        except:
            # LOG
            raise exceptions.APIException("shekast dar archive kardan contract.")

    def consider_escape_room(self, instance: BankRobbery):
        # TODO : Do not use random :(
        escape_rooms = EscapeRoom.objects.filter(state=0).all()

        if not escape_rooms:
            raise exceptions.APIException("kambode otagh farar.")

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
    BankPenetrationBaseViewSet
    ):

    queryset = BankRobbery.objects.all()
    serializer_class = BankRobberyListSerializer
    team_role_allowed = "Mafia"
    success_message_list = "Team Bank Robberies"
    success_message_deposit = "Box Opened"

    def get_serializer_class(self):
        if self.action == "list":
            return BankRobberyListSerializer
        elif self.action == "open_escape_room":
            return BankRobberyOpenSerializer
        elif self.action == "open_deposit_box":
            return BankRobberyOpenDepositBoxSerializer
        return serializers.Serializer

    def query(self, owner):
        return self.queryset.filter(mafia=owner).all()


    def perform_on_box(self, serializer):
        box = serializer.validated_data["deposit_box"]
        # box is selected box
        boxes = find_boxes(box)
        boxes = self.perform_on_boxes(serializer, boxes)
        box = self.select_box(boxes, box)
        # box is a random box. kind of random
        self.attach_box_and_room(box, serializer.instance.escape_room)
        self.transfer_money(serializer, box)
        self.notify(boxes)

    def perform_on_boxes(self, serializer, boxes):
        """do any perform on all boxes together"""
        mafia: Team = serializer.instance.mafia

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

    def notify(self, boxes):
        return super().notify()



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
        citizen: Team = robbery.citizen
        contract: Contract = robbery.contract
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

class WarehouseDepositBoxBaseViewSet(
    ABC,
    GenericViewSet
    ):

    @response
    @game_state(["Night"])
    def update(
        self,
        request,
        *args, **kwargs
    ):
        instance = self.get_object()
        serializer = self.get_serializer(instance,
                                         data=request.data,
                                         partial=True)
        
        serializer.is_valid(raise_exception=True)
        result_of_answer = self.check_answer(serializer)
        if result_of_answer:
            self.right_answer(serializer)
            return Response(
                data={
                    "message": "Successfully Answered!",
                    "data": [],
                    "result": None
                },
                status=status.HTTP_200_OK,
            )

        else:
            self.wrong_answer()
            return Response(
                data={
                    "message": "Wrong answer :(",
                    "data" : [],
                    "result": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )


    def check_answer(self,
                     serializer: DepositBoxRobberySerializer
                     )-> bool:
        player_answer   = serializer.validated_data["answer"].strip()
        real_answer     =  serializer.instance.lock_question.answer
        return player_answer == real_answer
    
    @abstractmethod
    def right_answer(self,
                     serializer: DepositBoxRobberySerializer
                     ) -> None:
        ...


    def wrong_answer(self) -> None:
        # i think there is nothing to do
        ...

    @abstractmethod
    def call_API(self, sensor):
        ...


class WarehouseDepositBoxRobberyViewSet(WarehouseDepositBoxBaseViewSet):

    serializer_class = DepositBoxRobberySerializer
    queryset = WarehouseBox.objects.filter(lock_state=0).all() 


    def right_answer(self, serializer: DepositBoxRobberySerializer) -> None:
        #transfer money and question to team
        #check sensor
        box: WarehouseBox = serializer.instance
        box.unlocker = serializer.validated_data["team"]
        box.lock_state = 1
        box.save()
        money_change_logger = MoneyChangeLogger.objects.create(
            from_team=None,
            to_team=team,
            amount=box.money,
            warehouse_box=box,
            before_wallet=team.wallet,
            current_wallet=None,
        )
        money_change_logger.save()
        team: Team = serializer.validated_data["team"]
        team.wallet += box.money
        box.box_question.last_owner = team
        TeamQuestionRel.objects.create(
            team=team,
            question=box.box_question
        )
        money_change_logger.current_wallet = team.wallet
        money_change_logger.save()
        team.save()
        box.box_question.save()
        
        if box.sensor_state:
            self.take_back_some_money(team=team, serializer=serializer)
        
        self.call_API(box.sensor_state)
            
    def take_back_some_money(
            self,
            box : WarehouseBox,
            team: Team
            )   -> None:
        try:
            conf = ConstantConfig.objects.last()
        except:
            #LOGGER :((
            raise exceptions.APIException(
                "Config instance not found. Call web master"
            )
        
        cost = box.worth * conf.penalty_percent //100
        team.wallet -= cost
        if team.wallet < 0:
            team.bank_liabilities += team.wallet * (-1)
            team.wallet = 0
        team.save()
    
    def call_API(self, sensor):
        if sensor:
            msg = "robbed and sensor activated"
        else:
            msg = "robbed"
        #TODO
            


class WarehouseDepositBoxHackCheckViewSet(WarehouseDepositBoxBaseViewSet):

    serializer_class = DepositBoxHackCheckSerializer
    queryset = WarehouseBox.objects.all() 

    def right_answer(self,
                     serializer: DepositBoxHackCheckSerializer
                     ) -> None:
        
        box: WarehouseBox = serializer.instance
        box.unlocker = serializer.validated_data["team"]
        box.lock_state = 2
        box.save()
        team: Team = serializer.validated_data["team"]
        c = box.money + int(box.box_question.price * 0.5)
        team.wallet += c
        team.save()
        self.call_API(box.sensor_state)
    
    def call_API(self, sensor):
        msg = "jabeh ba movafaghiat eemen shod"
        #TODO
            
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

    def choose_room(self) -> EscapeRoom:
        escape_rooms = EscapeRoom.objects.filter(state=0).all()

        if not escape_rooms:
            raise exceptions.APIException("kambode otagh farar.")

        # filter rooms to make sure
        # check no_valid_citizen
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

        
class BankSensorInstallViewSet(
    BankPenetrationBaseViewSet
):
    queryset = BankSensorInstall.objects.all()
    serializer_class = BankSensorInstallationListSerializer
    team_role_allowed = "Shahrvand"
    success_message_list = "Team Bank Robberies"


    def get_serializer_class(self):
        if self.action == "list":
            return BankSensorInstallationListSerializer
        elif self.action == "open_escape_room":
            return BankSensorInstallationOpenSerializer
        elif self.action == "open_deposit_box":
            return BankSensorInstallOpenDepositBox
        return serializers.Serializer

    def query(self, owner):
        return self.queryset.filter(citizen=owner).all() 

    def perform_on_box(self,
                       serializer : BankSensorInstallOpenDepositBox
                       )-> None:
        box : BankDepositBox = serializer.validated_data["deposit_box"]
        installation : BankSensorInstall = serializer.instance

        box.save(
            sensor_owner=installation.police,
            sensor_state=1
            )
        self.notify()
        self.transfer_money(installation)

    def transfer_money(self,
                       installation :BankSensorInstall
                       ) -> None:
        # FIXME
        # I'm not sure about what should I have to do, the document did not mention about this part.
        # as when you see this ,you know I'm not a part of the team anymore.
        # so you should write this function on your own to specify what will happen to the contract between police and citizen  
        # Best regards,
        # Amin Masoudi 
        ...
            
        
class WarehouseDepositBoxHackViewSet(WarehouseDepositBoxBaseViewSet):

    serializer_class = DepositBoxHackSerializer
    queryset = WarehouseBox.objects.all() 


    def right_answer(self, serializer: DepositBoxRobberySerializer) -> None:
        box: WarehouseBox = serializer.instance
        if not box.is_lock:
            self.operations_on_mafia(serializer)
            self.operations_on_police(serializer)
            # well done
            
        self.operations_on_box(serializer)

    def operations_on_box(self, serializer)-> None:
        box : WarehouseBox = serializer.instance
        box.sensor_state = True
        box.sensor_hacker = serializer.validated_data["team"]
        box.save()

    def operations_on_police(self, serializer):
        box : WarehouseBox = serializer.instance
        police :Team = serializer.validated_data["team"]
        conf = ConstantConfig.objects.last()
        bonus = box.worth * conf.bonus_percent //100
        police.wallet += bonus
        police.save()

    def operations_on_mafia(self, serializer):
        conf = ConstantConfig.objects.last()
        box : WarehouseBox = serializer.instance
        mafia : Team = box.unlocker

        cost = box.worth * conf.penalty_percent //100

        mafia.wallet -= cost
        if mafia.wallet < 0:
            mafia.bank_liabilities += mafia.wallet * (-1)
            mafia.wallet = 0
        mafia.save()


    def call_API(self, sensor):
        #TODO 
        ...


class FindCardViewSet(
    GenericViewSet,
    mixins.UpdateModelMixin
    ):
    serializer_class = FindCardSerializer
    queryset = Team.objects.filter(state="Active").all()

    @response
    @game_state()
    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response(
            data={
                "message": "OK",
                "data": ["AFARIN!. shoma kart ra yafti"],
                "result": None
            },
            status=status.HTTP_200_OK
        )

    def perform_update(self, serializer):
        serializer.save(has_card=True)