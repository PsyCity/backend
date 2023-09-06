from rest_framework import serializers
from rest_framework.exceptions import NotAcceptable, APIException
from core.models import Team, Player, PlayerRole, TeamJoinRequest
from rest_framework.exceptions import bad_request
class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = []


class TeamMemberSerializers(serializers.Serializer):
    todo        = serializers.ChoiceField(["add","delete"],
                                          required=False,
                                          write_only=True)

    role        = serializers.ChoiceField(choices=PlayerRole.ROLES_CHOICES,
                                          required=False,
                                          write_only=True)
    
    agreement   = serializers.ListField(required=True, write_only=True)

class TeamJoinRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeamJoinRequest
        fields = ["player", "team"]

    def validate_team(self, team):
        if (team.player_team.count() > 3):
           raise  NotAcceptable("team is full", 406)
        return team
    
    def validate_player(self, player):
        if player.team_id:
            raise NotAcceptable("player is not homeless")
        return player