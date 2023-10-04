from rest_framework import serializers
from core.models import Player

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

class BodyguardRequestSerializer(serializers.Serializer):
    team_id = serializers.IntegerField()
    amount = serializers.IntegerField()
    homeless_id = serializers.IntegerField()
        
class BodyguardApprovementSerializer(serializers.Serializer):
    second_part_id = serializers.IntegerField()
    contract_id = serializers.IntegerField()