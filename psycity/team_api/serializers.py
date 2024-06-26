from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import serializers, generics, exceptions

from core.models import (
    PlayerRole, 
    TeamJoinRequest, 
    Team, 
    TeamFeature,
    Player, 
    ConstantConfig, 
    BankDepositBox,
    EscapeRoom,
    Contract,
    BankRobbery,
    TeamQuestionRel,
    WarehouseBox,
    BankSensorInstall,
    Question,
)
from core.config import HIDDEN_ID_LEN
from team_api.utils import team_cost_validation, ModelSerializerAndABCMetaClass, question_validation, player_cost_validation
from datetime import timedelta
from abc import ABC, abstractmethod
from abc import ABC, abstractmethod, ABCMeta

class TeamMemberSerializer(serializers.Serializer):
    todo        = serializers.ChoiceField(["add","delete"],
                                          required=True,
                                          write_only=True)

    role        = serializers.IntegerField()
    
    agreement   = serializers.IntegerField(required=True, write_only=True)
    player_role_queryset = PlayerRole.objects.all()

    def update(self, instance, validated_data):
        todo = validated_data.get("todo")
        
        role_query = self.player_role_queryset.filter(pk=validated_data.get("role"))
        if not role_query:
            raise serializers.ValidationError('role na motabar')
        role = role_query.first()
        if todo == "add":
            team = instance.team
            players = team.player_team.all()
            
            players = list(
                filter(
                    lambda p : role in p.player_role.all(),
                    players
                )
            )

            map(
                lambda p : p.player_role.remove(role),
                players
                )
            instance.player_role.add(role)
        
        elif todo == "delete":
            instance.player_role.remove(role)
        
        else:
            exceptions.NotAcceptable(f"{todo} not an option for todo")

    def validate_role(self, role):
        role_query = self.player_role_queryset.filter(pk=role)
        if not role_query:
            raise serializers.ValidationError('role id namotabar')
        return role



class TeamJoinRequestSerializer(serializers.ModelSerializer):
    team_name = serializers.SerializerMethodField() 
    class Meta:
        model = TeamJoinRequest
        fields = ["id", "player", "team", "team_name"]

    def validate_team(self, team):
        if (team.player_team.count() > 3):
           raise  exceptions.NotAcceptable("team por ast", 406)
        return team
    
    def validate_player(self, player):
        # if player.team_id:
        #     raise exceptions.NotAcceptable("player is not homeless")
        return player
    
    def get_team_name(self, obj):
        return obj.team.name
    
class KillHomelessSerializer(serializers.Serializer):
    team_id = serializers.IntegerField()
    homeless_id = serializers.IntegerField()

    def validate_team_id(self, team_id):
        team = Team.objects.get(pk=team_id)
        if team.team_role != "Mafia":
            raise exceptions.NotAcceptable("Team Mafia mafia nist")
            
        return team


    def is_valid(self, *, raise_exception=False):
        self.conf = ConstantConfig.objects.last()
        return super().is_valid(raise_exception=raise_exception)
    
    def validate_homeless_id(self, id):
        player = Player.objects.get(pk=id)
        if player.status != "Bikhaanemaan":
            raise exceptions.NotAcceptable("bazicon Bikhaanemaan nist.")

        if player.last_assassination_attempt:
            self.check_last_assassination_attempt(player)

        return player
    
    def validate(self, attrs):
        if self.conf.game_current_state != 0:
            raise exceptions.NotAcceptable("Bad time to kill.")
        
        return super().validate(attrs)

    def check_last_assassination_attempt(self, player:Player):
        t = player.last_assassination_attempt + timedelta(minutes=self.conf.assassination_attempt_cooldown_time)
        if timezone.now() < t:
            raise exceptions.NotAcceptable("cool_down nagozashteh") 
        



class DepositBoxSensorReportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDepositBox
        fields = [
            "id",
            "money",
            "robbery_state",
            "sensor_state",
        ]


class EscapeRoomListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EscapeRoom
        exclude = (
            "bank_deposit_box",
            "created_date",
            "updated_date"
            )
        
class EscapeRoomReserve(serializers.ModelSerializer):
    team_id = serializers.IntegerField()

    class Meta:
        model = EscapeRoom
        fields = ["team_id"]

    def validate_team_id(self, attr):
        team = get_object_or_404(Team,pk=attr)
        print(team.name)
        if team.team_role != "Polis":
            raise exceptions.ValidationError("team police nist")
        return team
    
    def validate(self, attrs):
        
        if self.instance.state != 1:
            raise exceptions.NotAcceptable("otagh dara halat robbed state nist.")
        return attrs


class EscapeRoomAfterPuzzleSerializer(serializers.ModelSerializer):
    solved = serializers.BooleanField()

    class Meta:
        model = EscapeRoom
        fields = ("solved",)
    
class EscapeRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = EscapeRoom
        fields = []



def required(value, field_name):
    if value is None:
        raise serializers.ValidationError(f'{field_name} lazem ast')

class ContractRegisterSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    terms = serializers.CharField(required=False)
    class Meta:
        model = Contract
        fields = (
            "id",
            "first_party_team",
            "second_party_team",
            "first_party_player",
            "second_party_player",
            "contract_type",
            "question",
            "cost",
            "terms",
        )


    def get_id(self, obj):
        return obj.id
    
    
    def contract_type_validation(self, attrs):
        contract_type = attrs.get("contract_type")

        print('attrs', attrs)
        
        if contract_type == "question_ownership_transfer":
            first: Team = attrs.get("first_party_team")
            second: Team = attrs.get("second_party_team")
            question: Question = attrs.get("question")
            cost = attrs.get("cost")
            required(first, 'first_party_team')
            required(second, 'second_party_team')
            required(question, 'question')
            required(cost, 'cost')
            
            team_cost_validation(attrs.get("cost"), first)
            question_validation(attrs.get("question"), first)

            

        elif contract_type == "bank_rubbery_sponsorship":
            try:
                citizen_team: Team = attrs.get("first_party_team")

            except:
                raise exceptions.ValidationError("cant retrieve data.")

            team_cost_validation(attrs.get("cost"), citizen_team)

        elif contract_type == "bank_sensor_installation_sponsorship":
            try:
                citizen_team :Team = attrs.get("first_party_team")
            except:
                raise exceptions.NotAcceptable("eshkal dar create!!")

            team_cost_validation(attrs.get("cost"), citizen_team)

        elif contract_type == "homeless_solve_question":
            first = attrs.get("first_party_team")
            second = attrs.get("second_party_player")
            question: Question = attrs.get("question")
            required(first, 'first_party_team')
            required(second, 'second_party_player')
            required(question, 'question')

            if second.status != 'Bikhaanemaan':
                raise serializers.ValidationError(f'Second party player Bikhaanemaan nist!')
            if question.last_owner != first:
                raise serializers.ValidationError(f'malek soal first party team nist!')



        elif contract_type == "bodyguard_for_the_homeless":
            first: Team = attrs.get("first_party_team")
            second: Player = attrs.get("second_party_player")
            cost = attrs.get("cost")
            required(first, 'first_party_team')
            required(second, 'second_party_player')
            required(cost, 'cost')

            if first.team_role not in ['Polis', 'Shahrvand']:
                raise serializers.ValidationError(f'team Polis ya Shahrvand nist!')
            if second.status != 'Bikhaanemaan':
                raise serializers.ValidationError(f'player Bikhaanemaan nist!')
            
            player_cost_validation(cost, second)


        elif contract_type == "other":
            first: Team = attrs.get("first_party_team")
            second: Team = attrs.get("second_party_team")
            terms = attrs.get('terms')
            required(first, 'first_party_team')
            required(second, 'second_party_team')
            required(terms, 'terms')


    def validate(self, attrs):
        self.contract_type_validation(attrs)
        return attrs

class ContractSignSerializer(serializers.ModelSerializer):
    team = serializers.IntegerField()
    class Meta:
        model = Contract
        fields = (
            "team",
        )
    
    def validate_team(self, pk):
        if len(str(pk)) == HIDDEN_ID_LEN:
            team = Team.objects.get(hidden_id=pk)
        else:
            team = Team.objects.get(pk=pk)
        return team.pk
    
    def validate(self, attrs):

        self.type_validation()
        team = Team.objects.get(pk=attrs["team"])
        
        if self.instance.first_party_team != team and self.instance.second_party_team != team:
            raise exceptions.ValidationError(
                "team is not contract team"
                )
        
        return super().validate(attrs)
    
    def type_validation(self):

        valid_contract_type = [
            "question_ownership_transfer",
            "bank_rubbery_sponsorship",
            "bank_sensor_installation_sponsorship",
            "bodyguard_for_the_homeless",
            "other",
        ]
        
        contract = self.instance
        
        if contract.contract_type not in valid_contract_type:
            raise exceptions.NotAcceptable(
                f"Not valid endpoint for {contract.contract_type}."
                )

class ContractConfirmSerializer(serializers.ModelSerializer):
    team = serializers.IntegerField()
    class Meta:
        model = Contract
        fields = (
            "team",
        )
    
    def validate_team(self, pk):
        if len(str(pk)) == HIDDEN_ID_LEN:
            team = Team.objects.get(hidden_id=pk)
        else:
            team = Team.objects.get(pk=pk)
        return team.pk
    
    def validate(self, attrs):

        self.type_validation()
        team = Team.objects.get(pk=attrs["team"])

        if self.instance.first_party_confirm and self.instance.second_party_confirm:
            raise exceptions.ValidationError(
                "gharardad ghablan taeed shode ast."
            )
        
        if self.instance.first_party_team != team and self.instance.second_party_team != team:
            raise exceptions.ValidationError(
                "team is not contract team"
                )
        
        return super().validate(attrs)
    
    def type_validation(self):

        valid_contract_type = [
            "question_ownership_transfer",
            "bank_rubbery_sponsorship",
            "bank_sensor_installation_sponsorship",
            "bodyguard_for_the_homeless",
            "other",
        ]

        paid_contract_type = [
            "question_ownership_transfer",
            "bank_rubbery_sponsorship",
            "bank_sensor_installation_sponsorship",
            "bodyguard_for_the_homeless",
        ]
        
        contract = self.instance
        
        if contract.contract_type not in valid_contract_type:
            raise exceptions.NotAcceptable(
                f"Not valid endpoint for {contract.contract_type}."
                )   
        if contract.contract_type in paid_contract_type and contract.is_paid == False:
            raise exceptions.NotAcceptable(
                f"contract did not paid. pay it before"
                )            

        
class ContractPaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = []
    
    def validate(self, attrs):
        self.type_validation()
        self.cost_validation()
        return super().validate(attrs)


    def cost_validation(self):
        team_cost_validation(
            team=self.instance.first_party_team,
            cost=self.instance.cost
        )

    def type_validation(self):
        
        valid_contract_type = [
            "question_ownership_transfer",
            "bank_rubbery_sponsorship",
            "bank_sensor_installation_sponsorship",
            "bodyguard_for_the_homeless",
        ]
        
        contract = self.instance
        
        if contract.contract_type not in valid_contract_type:
            raise exceptions.NotAcceptable(
                f"Not valid endpoint for {contract.contract_type}."
                )
        
class ContractRejectSerializer(serializers.Serializer):
    contract_id = serializers.IntegerField(required=True)
    team_id = serializers.IntegerField(required=False)
    player_id = serializers.IntegerField(required=False)

    
    def validate(self, attrs):
        contract: Contract = attrs.get('contract_id', None)
        team= attrs.get('team_id', None)
        player: Player = attrs.get('player_id', None)
        required(contract, 'contract_id')
        if not team and not player:
            raise serializers.ValidationError('team ya player vared shavad!')
        
        if team:
            team_query = Team.objects.filter(hidden_id=team) | Team.objects.filter(channel_role=team)
            if not team_query:
                raise serializers.ValidationError('team paida nashod!')
            team = team_query.first().channel_role
        
        return super().validate(attrs)




class TeamContractListSerializer(serializers.ModelSerializer):
    first_party_team = serializers.SerializerMethodField()
    second_party_team = serializers.SerializerMethodField()
    class Meta:
        model = Contract
        fields = [
            "id",
            "first_party_team",
            "second_party_team",
            "contract_type",
            "cost",
            "terms",
            "state",
            "archive",
        ]    

    def to_representation(self, instance):
        return super().to_representation(instance)
    def get_first_party_team(self, obj):
        if obj.first_party_team:
            return str(obj.first_party_team.channel_role)
        return None
    def get_second_party_team(self, obj):
        if obj.second_party_team:
            return str(obj.second_party_team.channel_role)
        return None

    
class TeamQuestionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id',
            'level',
            'last_owner',
            'price',
            'score',
            'is_published',
            'title',
            'body',
            'qtype',
        ]    

    def to_representation(self, instance):
        return super().to_representation(instance)

class TeamMoneySerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    team = serializers.IntegerField()

    class Meta:
        model = Team
        fields = ["amount", "team"]

    def validate_amount(self, amount):
        if amount < 1:
            raise exceptions.ValidationError("amount kamtar as 1.")
        return amount


    def validate_team(self, pk):
        team = Team.objects.get(pk=pk)    
        return team

    def validate(self, attrs):
        self.check_bank_wallet(**attrs)
        self.check_bank_cooldown(attrs["team"])
        return attrs

    def check_bank_wallet(self, **kwargs):
        team: Team = kwargs["team"]
        if team.bank < kwargs["amount"]:
            raise exceptions.NotAcceptable("Amount bishtar as team's bank.")

    def check_bank_cooldown(self, team:Team):
        conf = ConstantConfig.objects.last()
        if not team.last_bank_action:
            return
        
        t = team.last_bank_action + timedelta(minutes=conf.team_bank_transaction_cooldown)
        if timezone.now() < t:
            raise exceptions.NotAcceptable("cooldown tamam nashode.")
        
class TeamMoneySerializerwtb(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    team = serializers.IntegerField()

    class Meta:
        model = Team
        fields = ["amount", "team"]

    def validate_amount(self, amount):
        if amount < 1:
            raise exceptions.ValidationError("amount kamtar as 1.")
        return amount


    def validate_team(self, pk):
        team = Team.objects.get(pk=pk)    
        return team

    def validate(self, attrs):
        self.check_bank_wallet(**attrs)
        self.check_bank_cooldown(attrs["team"])
        return attrs

    def check_bank_wallet(self, **kwargs):
        team: Team = kwargs["team"]
        if team.wallet < kwargs["amount"]:
            raise exceptions.NotAcceptable("Amount bishtar as team's wallet.")

    def check_bank_cooldown(self, team:Team):
        conf = ConstantConfig.objects.last()
        if not team.last_bank_action:
            return
        
        t = team.last_bank_action + timedelta(minutes=conf.team_bank_transaction_cooldown)
        if timezone.now() < t:
            raise exceptions.NotAcceptable("cooldown tamam nashode.")



class LoanSerializer(serializers.Serializer):
    team = serializers.IntegerField()
    amount = serializers.IntegerField()


    def validate_amount(self, amount):
        self.positive_amount(amount)
        return amount
    
    def validate_team(self, pk):
        team = Team.objects.get(pk=pk)
        return team


    def validate(self, attrs):
        self.bank_cooldown_validation(attrs["team"])
        self.max_team_loan_amount_validation(attrs["amount"],
                                             team=attrs["team"]
                                             )
        
        return super().validate(attrs)
    

    def bank_cooldown_validation(self, team):
        conf = ConstantConfig.objects.last()
        if not team.last_bank_action:
            return
          
        t = team.last_bank_action + timedelta(minutes=conf.team_bank_transaction_cooldown)
        if timezone.now() < t:
            raise exceptions.NotAcceptable("cooldown tamam nashode.")


    def max_team_loan_amount_validation(self, amount, team:Team):
        conf = ConstantConfig.objects.last()
        max_amount = team.bank * conf.team_loan_percent_max
        team.max_bank_loan = max_amount
        team.save()
        if amount > max_amount:
            raise exceptions.NotAcceptable("meqdaar bishtar as had-e aksar vaam momken.")
        
    def positive_amount(self, amount):
        if amount <= 0:
            raise exceptions.ValidationError("amount is less then or equal zero.")


class LoanRepaySerializer(LoanSerializer):
    def validate(self, attrs):
        self.bank_cooldown_validation(attrs["team"])
        self.wallet_validation(attrs)
        return attrs


    def wallet_validation(self, attrs):
        team :Team = attrs["team"]
        if team.wallet < attrs["amount"]:
            raise exceptions.NotAcceptable(detail="team poll nadarad.")
        
class BankRobberyWaySerializer(serializers.ModelSerializer):
    class Meta:
        model = BankRobbery
        fields = [
            "mafia",
            "contract"
        ] 

    def validate_contract(self, contract):
        if contract.contract_type != "bank_rubbery_sponsorship":
            raise exceptions.ValidationError("noe garardad  bank_rubbery_sponsorship nist")

        if contract.state != 2:
            raise exceptions.ValidationError("Contract state eshtebah.")
        if contract.archive:
            raise exceptions.NotAcceptable("gharardad Archive shode.")
        return contract
    
    def validate_mafia(self, team:Team):
        if team.team_role != "Mafia":
            raise exceptions.ValidationError("team mafia nist")
        
        self.validate_mafia_max_escape_room(team)
        
        return team 

    def validate(self, attrs):
        return super().validate(attrs)
        
    def validate_mafia_max_escape_room(self, mafia:Team):
        
        profile = mafia.team_feature.first()
        if not profile:
            profile = TeamFeature.objects.create(team=mafia)
            
        conf = ConstantConfig.objects.last()

        if not profile.mafia_reserved_escape_room < conf.team_escape_room_max:
            raise exceptions.NotAcceptable("mahdodiat team_escape_room")


class BankRobberyListSerializer(serializers.ModelSerializer):

    citizen_id = serializers.CharField(source="citizen.pk")
    citizen_name = serializers.CharField(source="citizen.name")
    mafia_id = serializers.CharField(source="mafia.pk")
    mafia_name = serializers.CharField(source="mafia.name")
    robbery_id = serializers.IntegerField(source="id")
    

    class Meta:
        model = BankRobbery
        fields = [
            "robbery_id",
            "state",
            "citizen_id",
            "citizen_name",
            "mafia_id",
            "mafia_name",
            "escape_room"
            ]


class BankPenetrationOpenSerializer(serializers.ModelSerializer):

    obj_name = ""

    def validate(self, attrs):
        if self.instance.state != 1:
            raise exceptions.NotAcceptable(f"{self.obj_name} is on state {self.instance.state}")
        return super().validate(attrs)
    
    
class BankRobberyOpenSerializer(BankPenetrationOpenSerializer):
    obj_name = "BankRobbery"
    class Meta:
        model = BankRobbery
        fields = []


class BankPenetrationOpenDepositBoxSerializer(   
    ABC,
    serializers.ModelSerializer,
    metaclass=ModelSerializerAndABCMetaClass
    ):
    deposit_box = serializers.IntegerField()
    

    def validate_deposit_box(self, pk):
        try:
            box = BankDepositBox.objects.get(pk=pk)
        except:
            raise exceptions.NotFound("Box paida nashod.")
        return box
    

    def check_deposit_box(self, box:BankDepositBox):
        if box.robbery_state:
            raise exceptions.NotAcceptable("pol as box dozdideh shod.")

    def __deadline_check(self):
        room = self.query()
        solve_time = room.solve_time
        if timezone.now() > (self.instance.opening_time + timedelta(minutes=solve_time)):
            self.save(state=4)
            raise exceptions.NotAcceptable("Expired escape room.")
        return True
    
    @abstractmethod
    def query(self):
        ...

    def check_password(self):
        ...

    def is_acceptable(self):
        self.__deadline_check()
        self.check_deposit_box(self.validated_data["deposit_box"])
        self.check_password(self.validated_data["password"])


class ModelSerializerAndABCMetaClass(
    type(serializers.ModelSerializer),
    ABCMeta
    ): ...


class DepositBoxSolveSerializer(
    ABC,
    serializers.ModelSerializer,
    metaclass=ModelSerializerAndABCMetaClass
    ):

    answer  = serializers.CharField()
    team    = serializers.IntegerField()
    
    class Meta:
        model   = WarehouseBox
        fields  = "answer", "team"


    @abstractmethod
    def validate(self, attrs):
        return attrs

    @abstractmethod
    def validate_team(self, pk):
        ...

        
class DepositBoxRobberySerializer(DepositBoxSolveSerializer):
    
    
    def validate(self, attrs):
        if not self.instance.is_lock:
            raise exceptions.NotAcceptable(
                "box khalist!"
            )
        return super().validate(attrs)
    
    def validate_team(self, pk):
        team = Team.objects.get(pk=pk)  #TODO: team is mafia
        if team.team_role != "Mafia":
            raise exceptions.ValidationError(
                "Team mafia nist"
            )
        if not team.has_card:
            raise exceptions.NotAcceptable(
                "Shooma cart nadarii"
            )
        return team
    
class DepositBoxHackSerializer(DepositBoxSolveSerializer):

    def validate(self, attrs):
        if self.instance.lock_state == 2:
            raise exceptions.NotAcceptable(
                "Oops!, box na motabar."
            )
        if self.instance.sensor_state:
            raise exceptions.NotAcceptable(
                "ghablan hack shode"
            )
        return super().validate(attrs)
    
    def validate_team(self, pk):
        team = Team.objects.get(pk=pk)  #TODO: team is Police
        if team.team_role != "Polis":
            raise exceptions.ValidationError(
                "Team Polis nist!"
            )
        if not team.has_card:
            raise exceptions.NotAcceptable(
                "Shooma cart nadarii"
            )
        return team

class DepositBoxHackCheckSerializer(DepositBoxSolveSerializer):

    def validate(self, attrs):
        if self.instance.lock_state != 0:
            raise exceptions.NotAcceptable(
                "Oops!, box na motabar."
            )
        return super().validate(attrs)
    
    def validate_team(self, pk):
        team = Team.objects.get(pk=pk)  #TODO: team is Citizen
        if team.team_role != "Shahrvand":
            raise exceptions.ValidationError(
                "Team Shahrvand nist!"
            )
        if not team.has_card:
            raise exceptions.NotAcceptable(
                "Shooma cart nadarii"
            )
        return team

 


class BankRobberyOpenDepositBoxSerializer(
    BankPenetrationOpenDepositBoxSerializer
    ):
    password    = serializers.IntegerField()

    class Meta:
        model = BankRobbery
        fields = [
            "deposit_box",
            "password"
            ]
        

    def check_deposit_box(self, box: BankDepositBox):
        super().check_deposit_box(box)
        if box.money == 0 :
            raise exceptions.NotAcceptable("box khali. yeki digeh entekab kon.")
    
    def check_password(self, password):
        if password != self.validated_data["deposit_box"].password:
            raise exceptions.NotAcceptable("Passworde eshtebah")

    def query(self) -> EscapeRoom:
        return self.instance.escape_room


class BankSensorInstallOpenDepositBox(
    BankPenetrationOpenDepositBoxSerializer
    ):
    class Meta:
        model  = BankSensorInstall
        fields = "deposit_box",

    def check_deposit_box(self, box: BankDepositBox):
        super().check_deposit_box(box)
        if box.sensor_state == 1:
            raise exceptions.NotAcceptable("Sensor ghablan nasb shode. eki digeh entekhab kon")
        
    def query(self):
        return self.instance.room

class BankSensorInstallWaySerializer(
    serializers.ModelSerializer
):
    team = serializers.IntegerField()

    class Meta:
        model = BankSensorInstall
        fields = "contract", "team"

    def is_valid(self, *, raise_exception=False):
        return super().is_valid(raise_exception=raise_exception)

    def validate_contract(self, contract):
        if contract.contract_type != "bank_sensor_installation_sponsorship":
            raise exceptions.ValidationError("gharardad nooee eshtebah")
        if BankSensorInstall.objects.filter(contract=contract).last():
            raise exceptions.NotAcceptable("gharardad estefadeh shode")
        return contract

    def validate_team(self, team) ->Team:
        team = Team.objects.get(pk=team)
        if team.team_role == "Shahrvand":
            return team
        raise exceptions.ValidationError("Shahrvand nist!")
    
    def is_acceptable(self):
        self.check_room_usage_of_team()
        self.check_contract_and_team()

    def check_contract_and_team(self):
        team : Team = self.validated_data["team"]
        contract :Contract = self.validated_data["contract"]
        if contract.second_party_team != team:
            raise exceptions.NotAcceptable("OOPS!!, team second_party_team gharardad nist")

    def check_room_usage_of_team(self):
        citizen : Team= self.validated_data["team"]
        profile = citizen.team_feature.first()
        if not profile:
            profile = TeamFeature.objects.create(team=citizen)
        conf = ConstantConfig.objects.last()

        if not profile.citizen_opened_night_escape_rooms < conf.team_escape_room_max:
            raise exceptions.NotAcceptable("mahdodiat team_escape_room")
        

    def save(self, **kwargs):

        kwargs["citizen"] = self.validated_data["team"]
        kwargs["contract"] = self.validated_data["contract"]
        assert self.validated_data["contract"].first_party_team.team_role == "Polis"
        kwargs["police"] = self.validated_data["contract"].first_party_team
        self.instance = self.create(kwargs)
        assert self.instance is not None, (
            '`create()` did not return an object instance.'
        )
        return self.instance


class BankSensorInstallationListSerializer(serializers.ModelSerializer):

    citizen_id  = serializers.IntegerField(source="citizen.id")
    citizen_name = serializers.CharField(source="citizen.name")
    police_id   = serializers.IntegerField(source="police.id")
    police_name  = serializers.CharField(source="police.name")
    request_id  = serializers.IntegerField(source="id")

    class Meta:
        model = BankSensorInstall
        fields = [
            "request_id",
            "state",
            "citizen_id",
            "citizen_name",
            "police_id",
            "police_name",
            "room"
            ]
        
class BankSensorInstallationOpenSerializer(
    BankPenetrationOpenSerializer
    ):
    obj_name = "Installation request"
    class Meta:
        model = BankSensorInstall
        fields = []



class QuestionBuySerializer(serializers.Serializer):
    team_id = serializers.IntegerField()
    question_id = serializers.IntegerField()


class QuestionSolveSerializer(serializers.Serializer):
    question_type = serializers.IntegerField()
    question_id = serializers.IntegerField()
    team_id = serializers.IntegerField(required=False)
    player_id = serializers.IntegerField(required=False)
    text_answer = serializers.CharField(required=False)
    file_answer = serializers.FileField(required=False)

    def validate(self, attrs):
        question_type = attrs.get("question_type")
        team_id = attrs.get("team_id")
        player_id = attrs.get("player_id")
        text_answer = attrs.get("text_answer")
        file_answer = attrs.get("file_answer")

        # Validate that at least one of team_id and player_id is provided
        if not team_id and not player_id:
            raise serializers.ValidationError("team_id ya player_id ra faraham konid")
        
        if question_type == 1:
            if not text_answer:
                raise serializers.ValidationError("text_answer lazem ast baraye question_type 1")
        elif question_type == 2:
            if not file_answer:
                raise serializers.ValidationError("file_answer lazem ast baraye question_type 2")
        else:
            raise serializers.ValidationError('Invalid question_type')

        return attrs



class FindCardSerializer(
    serializers.ModelSerializer
):
    
    class Meta:
        model = Team
        fields = []



class QuestionRelSerializer(
    serializers.ModelSerializer
):
    question = TeamQuestionListSerializer()
    class Meta:
        model = TeamQuestionRel
        fields = "id", "solved", "question"



class TeamPropertySerializer(
    serializers.ModelSerializer
):
    # questions = serializers.SerializerMethodField()
    teamquestionrel_team = QuestionRelSerializer(many=True)
    class Meta:
        model = Team
        fields = "pk", "has_card", "teamquestionrel_team", "wallet"
