from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from core.models import Player, TeamJoinRequest

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = []

class TeamJoinRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamJoinRequest
        fields = ["player_id", "team_id", "state"]
        extra_kwargs = {'player_id': {'read_only': True},
                        'team_id' : {'read_only' : True},
                        'state' : {'read_only' : True}}

    def update(self, instance, validated_data):
        team    = instance.team_id
        player  = instance.player_id
        if instance.state =="inactive":
            raise ValidationError("Join request has been expired")
        if player.team_id:
            raise ValidationError("player has a team")
        if player.status == "Dead":
            raise ValidationError("The player is Dead")
        if len(team.player_team.all()) > 3:
            raise ValidationError("team is full")

        player.status = "TeamMember"
        player.team_id = team
        player.player_role.clear()
        player.save()

        instance.state = "inactive"
        instance.save()

        return instance
        
        