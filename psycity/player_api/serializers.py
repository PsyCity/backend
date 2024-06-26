from rest_framework import serializers
from core.models import Player, Contract, Question, PlayerQuestionRel
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
        if team.team_role != "Polis":
            raise  exceptions.ValidationError("Polis nist")
        return team
    
    def validate_second_party_player(self, player):
        if player.status != "Bikhaanemaan":
            raise exceptions.ValidationError("bazicon Bikhaanemaan nist")
        return player
    
    def validate(self, attrs):
        if attrs["second_party_player"].wallet < attrs["cost"]:
            raise exceptions.NotAcceptable("bishtar as bodjeh Bikhaanemaan") 
        return super().validate(attrs) 

class LoginSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Player
        fields = "discord_username" ,"password"


class PlayerContractListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = [
            "id",
            "first_party_team",
            "second_party_team",
            "contract_type",
            "cost",
            "terms",
            "state",
            "archive",
        ]    

    def to_representation(self, instance):
        return super().to_representation(instance)
    
class PlayerQuestionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id',
            'level',
            'last_owner',
            'price',
            'score',
            'is_published',
            'title',
            'body',
            'qtype',
        ]    

    def to_representation(self, instance):
        return super().to_representation(instance)

class PlayerQuestionRelSerializer(
    serializers.ModelSerializer
):
    question = PlayerQuestionListSerializer()
    class Meta:
        model = PlayerQuestionRel
        fields = "id", "solved", "question"

class PlayerPropertySerializer(
    serializers.ModelSerializer
):
    playerquestionrel_player = PlayerQuestionRelSerializer(many=True)
    class Meta:
        model = Player
        fields = "pk", "playerquestionrel_player" 


