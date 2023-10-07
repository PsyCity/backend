from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from core.models import (
    Team,
    Question,
    Contract,
    Player,
)
class TeamListSerializer(ModelSerializer):
    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "state"
        ]

class TeamRetrieveSerializer(ModelSerializer):
    players = serializers.SerializerMethodField()
    class Meta:
        model = Team
        fields = "__all__"

    def get_players(self, obj):
        players = obj.player_team.all()
        players = list(map(lambda player: player.pk, players))
        return players

class QuestionListSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "pk",
            "title",
            "qtype"
        ]

class QuestionRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Question
        exclude = [
            "answer_text",
            "answer_file",
        ]



class ContractListSerializer(ModelSerializer):
    class Meta:
        model = Contract
        fields = [
            "id",
            "contract_type",
            "first_party_agree",
            "second_party_agree"
        ]

class ContractRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Contract
        fields = "__all__"


class PlayerListSerializer(ModelSerializer):
    roles = serializers.SerializerMethodField()
    class Meta:
        model = Player
        fields = [
            "id",
            "first_name",
            "last_name",
            "team",
            "status",
            "roles"
        ]
    def get_roles(self, obj):
        roles = obj.player_role.all()
        roles = list(map(lambda role: role.name, roles))

        return roles

class PlayerRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Player
        fields = "__all__"