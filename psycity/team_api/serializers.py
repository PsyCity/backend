from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.exceptions import NotAcceptable
from core.models import  PlayerRole, TeamJoinRequest

class TeamMemberSerializer(serializers.Serializer):
    todo        = serializers.ChoiceField(["add","delete"],
                                          required=False,
                                          write_only=True)

    role        = serializers.ChoiceField(choices=PlayerRole.ROLES_CHOICES,
                                          required=False,
                                          write_only=True)
    
    agreement   = serializers.IntegerField(required=True, write_only=True)

    def update(self, instance, validated_data):
        todo = validated_data.get("todo")
        
        role = get_object_or_404(
            PlayerRole,
            name=validated_data.get("role")
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
            NotAcceptable(f"{todo} not an option for todo")




class TeamJoinRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeamJoinRequest
        fields = ["id", "player", "team"]

    def validate_team(self, team):
        if (team.player_team.count() > 3):
           raise  NotAcceptable("team is full", 406)
        return team
    
    def validate_player(self, player):
        if player.team_id:
            raise NotAcceptable("player is not homeless")
        return player