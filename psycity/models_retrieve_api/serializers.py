from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from core.models import (
    Team,
    Question,
    Contract,
    WarehouseBox,
    WarehouseQuestions,
    Player,
)
class TeamListSerializer(ModelSerializer):
    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "state",
            "team_role",
            "wallet",
            "total_asset",
            "level",
            "channel_id",
            "channel_role",
        ]
class TeamPlayerSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = [
            "id",
            "name",
            "discord_username",
            "roles"
                  ]
    def get_name(self, player):
        return player.__str__()
    
    def get_roles(self, obj):
        roles = obj.player_role.all()
        roles = list(map(lambda role: role.pk, roles))

        return roles


class TeamRetrieveSerializer(ModelSerializer):
    players = serializers.SerializerMethodField()
    class Meta:
        model = Team
        fields = "__all__"

    def get_players(self, obj):
        players = obj.player_team.all()
        players_serializer = TeamPlayerSerializer(players, many=True)
        return players_serializer.data


class QuestionListSerializer(ModelSerializer):
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
            'no_valid_tries',
            'valid_solve_minutes',
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
            "first_party_team",
            "second_party_team",
            "contract_type",
            "cost",
            "terms",
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
            "discord_username",
            "team",
            "status",
            "roles"
        ]
    def get_roles(self, obj):
        roles = obj.player_role.all()
        roles = list(map(lambda role: role.pk, roles))

        return roles

class PlayerRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Player
        fields = "__all__"


class WarehouseBoxListSerializer(
    ModelSerializer
    ):

    class Meta:
        model = WarehouseBox
        fields = "id", "is_lock" 

class WarehouseQuestionSerializer(
    ModelSerializer
    ):
    class Meta:
        model   = WarehouseQuestions
        fields  = "text",

class WarehouseBoxRetrieveSerializer(
    ModelSerializer
    ):
    lock_question = WarehouseQuestionSerializer()
    class Meta:
        model   = WarehouseBox
        fields  = (
            "id",
            "is_lock",
            "lock_question"
        )