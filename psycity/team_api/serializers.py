from rest_framework import serializers
from core.models import Team, Player, Role
from rest_framework.exceptions import bad_request
class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = []


class TeamMemberSerializers(serializers.Serializer):
    player_id   = serializers.IntegerField()
    team_id     = serializers.IntegerField()
    todo        = serializers.ChoiceField(["add","delete"], required=False)
    role        = serializers.ChoiceField(choices=Role.RoleChoices,
                                          required=False)
    agreement   = serializers.ListField()

    @property
    def team(self):
        team_id = self.validated_data.get("team_id")
        instance = Team.objects.filter(pk=team_id).first()
        return instance
    
    @property
    def player(self):
        player_id = self.validated_data.get("player_id")
        obj = Player.objects.filter(pk=player_id).first()
        return obj

    def update(self, instance, validated_data):
        if self.data["role"]:
            self.role_update(instance, validated_data)

        return instance
    def role_update(self, team:Team, validated_data):
        player = self.player
        
        role = validated_data.get("role")
        role = Role.objects.get(name=role)

        todo = validated_data.get("todo")

        if todo == "add":
            players = team.player_team.all()
            players = list(filter(lambda p: role in p.player_role.all(), players))
            map(lambda p: p.player_role.remove(role),players)

            player.player_role.add(role)
        
        elif todo=="delete":
            player.player_role.remove(role)
        