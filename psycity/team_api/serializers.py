from rest_framework import serializers
from core.models import Team, Player, PlayerRole
from rest_framework.exceptions import bad_request
class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = []


class TeamMemberSerializers(serializers.Serializer):
    todo        = serializers.ChoiceField(["add","delete"], required=False)

    role        = serializers.ChoiceField(choices=PlayerRole.ROLES_CHOICES,
                                          required=False)
    agreement   = serializers.ListField(required=True)

    team_id     = serializers.IntegerField(allow_null=True)
