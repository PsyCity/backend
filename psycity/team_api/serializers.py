from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import serializers
from rest_framework import exceptions

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
    BankSensorInstall,
)
from team_api.utils import cost_validation
from datetime import timedelta


class TeamMemberSerializer(serializers.Serializer):
    todo        = serializers.ChoiceField(["add","delete"],
                                          required=False,
                                          write_only=True)

    role        = serializers.ChoiceField(choices=[1,2,3],
                                          required=False,
                                          write_only=True)
    
    agreement   = serializers.IntegerField(required=True, write_only=True)

    def update(self, instance, validated_data):
        todo = validated_data.get("todo")
        
        role = get_object_or_404(
            PlayerRole,
            pk=validated_data.get("role")
        )
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




class TeamJoinRequestSerializer(serializers.ModelSerializer):
    team_name = serializers.SerializerMethodField() 
    class Meta:
        model = TeamJoinRequest
        fields = ["id", "player", "team", "team_name"]

    def validate_team(self, team):
        if (team.player_team.count() > 3):
           raise  exceptions.NotAcceptable("team is full", 406)
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
            raise exceptions.NotAcceptable("Team is not Mafia")
            
        return team


    def is_valid(self, *, raise_exception=False):
        self.conf = ConstantConfig.objects.last()
        return super().is_valid(raise_exception=raise_exception)
    
    def validate_homeless_id(self, id):
        player = Player.objects.get(pk=id)
        if player.status != "Homeless":
            raise exceptions.NotAcceptable("Player is not homeless.")

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
            raise exceptions.NotAcceptable("cool_down has not passed") 
        



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
        if team.team_role != "Police":
            raise exceptions.ValidationError("Not a police Team")
        return team
    
    def validate(self, attrs):
        
        if self.instance.state != 1:
            raise exceptions.NotAcceptable("Room is not in robbed state.")
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



def required(value):
    if value is None:
        raise serializers.ValidationError('This field is required')

class ContractRegisterSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    class Meta:
        model = Contract
        fields = (
            "id",
            "first_party_team",
            "second_party_team",
            "contract_type",
            "cost",
            "terms",
        )

    def base_team_validation(self, team_id):
        required(team_id)
        return team_id

    def get_id(self, obj):
        return obj.id
    
    def validate_first_party_team(self, team_id):
        self.base_team_validation(team_id)
        return team_id
    
    def validate_second_party_team(self, team_id):
        self.base_team_validation(team_id)        
        return team_id
    
    def contract_type_validation(self, attrs):
        contract_type = attrs.get("contract_type")
        
        if contract_type == "question_ownership_transfer":
            first = attrs.get("first_party_team")
            cost_validation(attrs.get("cost"), first)

        elif contract_type == "bank_rubbery_sponsorship":
            try:
                citizen_team: Team = attrs.get("first_party_team")

            except:
                raise exceptions.ValidationError("cant retrieve data.")

            cost_validation(attrs.get("cost"), citizen_team)

        elif contract_type == "bank_sensor_installation_sponsorship":
            try:
                citizen_team :Team = attrs.get("first_party_team")
            except:
                raise exceptions.NotAcceptable("cant create!!")

            cost_validation(attrs.get("cost"), citizen_team)

        elif contract_type == "bodyguard_for_the_homeless":
            raise exceptions.NotAcceptable("Not this endpoint")

        elif contract_type == "other":
            raise exceptions.NotAcceptable("Not Implemented in here :)")


    def validate(self, attrs):
        self.contract_type_validation(attrs)
        return attrs

class ContractApprovementSerializer(serializers.ModelSerializer):
    team = serializers.IntegerField()
    class Meta:
        model = Contract
        fields = (
            "team",
        )
    
    def validate_team(self, pk):
        team = Team.objects.get(pk=pk)
        return team.pk
    
    def validate(self, attrs):

        self.type_validation()
        team = Team.objects.get(pk=attrs["team"])
        
        if self.instance.second_party_team != team:
            raise exceptions.ValidationError(
                "team is not contract team"
                )
        
        return super().validate(attrs)
    
    def type_validation(self):

        valid_contract_type = [
            "question_ownership_transfer",
            "bank_rubbery_sponsorship",
            "bank_sensor_installation_sponsorship"
        ]
        
        contract = self.instance
        
        if contract.contract_type not in valid_contract_type:
            raise exceptions.NotAcceptable(
                f"Not valid endpoint for {contract.contract_type}."
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
        cost_validation(
            team=self.instance.first_party_team,
            cost=self.instance.cost
        )

    def type_validation(self):
        
        valid_contract_type = [
            "question_ownership_transfer",
            "bank_rubbery_sponsorship",
            "bank_sensor_installation_sponsorship"
        ]
        
        contract = self.instance
        
        if contract.contract_type not in valid_contract_type:
            raise exceptions.NotAcceptable(
                f"Not valid endpoint for {contract.contract_type}."
                )

class TeamMoneySerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    team = serializers.IntegerField()

    class Meta:
        model = Team
        fields = ["amount", "team"]

    def validate_amount(self, amount):
        if amount < 1:
            raise exceptions.ValidationError("amount is less then 1.")
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
            raise exceptions.NotAcceptable("Amount is more then team's bank.")

    def check_bank_cooldown(self, team:Team):
        conf = ConstantConfig.objects.last()
        if not team.last_bank_action:
            return
        
        t = team.last_bank_action + timedelta(minutes=conf.team_bank_transaction_cooldown)
        if timezone.now() < t:
            raise exceptions.NotAcceptable("cooldown has not passed.")



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
            raise exceptions.NotAcceptable("cooldown has not passed.")


    def max_team_loan_amount_validation(self, amount, team:Team):
        conf = ConstantConfig.objects.last()
        max_amount = team.bank * conf.team_loan_percent_max
        team.max_bank_loan = max_amount
        team.save()
        if amount > max_amount:
            raise exceptions.ValidationError("amount is more then team's max loan amount.")
        
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
            raise exceptions.NotAcceptable(detail="Not enough money in teams wallet.")
        
class BankRobberyWaySerializer(serializers.ModelSerializer):
    class Meta:
        model = BankRobbery
        fields = [
            "mafia",
            "contract"
        ] 

    def validate_contract(self, contract):
        if contract.contract_type != "bank_rubbery_sponsorship":
            raise exceptions.ValidationError("Contract type is not bank_rubbery_sponsorship")

        if contract.state != 2:
            raise exceptions.ValidationError("Contract state is not valid.")
        if contract.archive:
            raise exceptions.NotAcceptable("Contract is Archived.")
        return contract
    
    def validate_mafia(self, team:Team):
        if team.team_role != "Mafia":
            raise exceptions.ValidationError("Not a mafia team")
        
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
            raise exceptions.NotAcceptable("team_escape_room limit")


class BankRobberyListSerializer(serializers.ModelSerializer):

    citizen_id = serializers.IntegerField(source="citizen.id")
    citizen_name = serializers.CharField(source="citizen.name")
    mafia_id = serializers.IntegerField(source="mafia.id")
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



class BankRobberyOpenDepositBoxSerializer(serializers.ModelSerializer):
    deposit_box = serializers.IntegerField()
    password    = serializers.IntegerField()

    class Meta:
        model = BankRobbery
        fields = [
            "deposit_box",
            "password"
            ]
        
    def validate_deposit_box(self, pk):
        try:
            box = BankDepositBox.objects.get(pk=pk)
        except:
            raise exceptions.NotFound("Box not found.")
        return box
    
    def check_deposit_box(self, box:BankDepositBox):

        if box.robbery_state:
            raise exceptions.NotAcceptable("Money has been stolen from the box.")
        if box.money == 0 :
            raise exceptions.NotAcceptable("Empty box. try another one.")    
    
    def check_password(self, password):
        if password != self.validated_data["deposit_box"].password:
            raise exceptions.NotAcceptable("Password Not match")

    def deadline_check(self):
        solve_time = self.instance.escape_room.solve_time
        if timezone.now() > (self.instance.opening_time + timedelta(minutes=solve_time)):
            self.save(state=4)
            raise exceptions.NotAcceptable("Expired escape room.")
        return True
    
    def is_acceptable(self):
        self.deadline_check()
        self.check_deposit_box(self.validated_data["deposit_box"])
        self.check_password(self.validated_data["password"])


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
            raise exceptions.ValidationError("Not a valid type contract")
        if BankSensorInstall.objects.filter(contract=contract).last():
            raise exceptions.NotAcceptable("Contract used")
        return contract

    def validate_team(self, team) ->Team:
        team = Team.objects.get(pk=team)
        if team.team_role == "Citizen":
            return team
        raise exceptions.ValidationError("Not Citizen!")
    
    def is_acceptable(self):
        self.check_room_usage_of_team()
        self.check_contract_and_team()

    def check_contract_and_team(self):
        team : Team = self.validated_data["team"]
        contract :Contract = self.validated_data["contract"]
        if contract.second_party_team != team:
            raise exceptions.NotAcceptable("OOPS!!, team is not contract's second_party_team ")

    def check_room_usage_of_team(self):
        citizen : Team= self.validated_data["team"]
        profile = citizen.team_feature.first()
        if not profile:
            profile = TeamFeature.objects.create(team=citizen)
        conf = ConstantConfig.objects.last()

        if not profile.citizen_opened_night_escape_rooms < conf.team_escape_room_max:
            raise exceptions.NotAcceptable("team_escape_room limit")
        

    def save(self, **kwargs):

        kwargs["citizen"] = self.validated_data["team"]
        kwargs["contract"] = self.validated_data["contract"]
        assert self.validated_data["contract"].first_party_team.team_role == "Police"
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

