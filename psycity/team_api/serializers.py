from rest_framework import serializers
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

