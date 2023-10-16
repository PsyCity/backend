from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework import exceptions

from core.models import  PlayerRole, TeamJoinRequest, Team, Player, ConstantConfig, BankDepositBox

from datetime import timedelta
from django.utils import timezone
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