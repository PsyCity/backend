from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import serializers
from rest_framework import exceptions

from core.models import (
    PlayerRole, 
    TeamJoinRequest, 
    Team, 
    Player, 
    ConstantConfig, 
    BankDepositBox,
    EscapeRoom,
    Contract,
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
            second = attrs.get("second_party_team")
            cost_validation(attrs.get("cost"), second)

        elif contract_type == "bank_rubbery_sponsorship":
            try:
                citizen_team: Team = attrs.get("second_party_team")

            except:
                raise exceptions.ValidationError("cant retrieve data.")

            cost_validation(attrs.get("cost"), citizen_team)

        elif contract_type == "bank_sensor_installation_sponsorship":
            ...

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
        