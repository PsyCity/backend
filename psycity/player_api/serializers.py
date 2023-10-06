from rest_framework import serializers
from core.models import Player, Contract
from rest_framework import exceptions
class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = []
class DiscordPlayer(serializers.Serializer):
    discord = serializers.CharField()


class LoanReceiveSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
    amount = serializers.IntegerField()
    
class LoanRepaymentSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
    amount = serializers.IntegerField()


class BodyguardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = (
            "first_party_team",
            "second_party_player",
            "cost"
        )

    
    def validate_first_party_team(self, team):
        if team.team_role != "Police":
            raise  exceptions.ValidationError("Not a police team")
        return team
    
    def validate_second_party_player(self, player):
        if player.status != "Homeless":
            raise exceptions.ValidationError("Not a homeless player")
        return player
    
    def validate(self, attrs):
        if attrs["second_party_player"].wallet < attrs["cost"]:
            raise exceptions.NotAcceptable("Out of homeless budget") 
        return super().validate(attrs) 
