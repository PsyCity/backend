from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from core.models import (
    Team,
    Question,
    Contract,
    WarehouseBox,
    ConstantConfig,
    WarehouseQuestions,
    TeamQuestionRel,
    Player,
)
class TeamListSerializer(ModelSerializer):
    channel_role = serializers.CharField()
    channel_id = serializers.CharField()
    class Meta:
        model = Team
        fields = [
            "name",
            "state",
            "team_role",
            "wallet",
            "total_asset",
            "level",
            "channel_id",
            "channel_role",
            "hidden_id",
        ]
    def get_channel_role(self, obj):
        return str(obj.channel_role)
    
    def get_channel_id(self, obj):
        return str(obj.channel_id)

class TeamPlayerSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    discord_id = serializers.CharField()

    class Meta:
        model = Player
        fields = [
            "name",
            "discord_username",
            "discord_id",
            "roles"
            ]
    def get_name(self, player):
        return player.__str__()
    
    def get_roles(self, obj):
        roles = obj.player_role.all()
        roles = list(map(lambda role: role.pk, roles))

        return roles
    
    def get_discord_id(self, obj):
        return str(obj.discord_id)


class TeamRetrieveSerializer(ModelSerializer):
    players = serializers.SerializerMethodField()
    channel_role = serializers.CharField()
    channel_id = serializers.CharField()
    class Meta:
        model = Team
        fields = "__all__"

    def get_players(self, obj):
        players = obj.player_team.all()
        players_serializer = TeamPlayerSerializer(players, many=True)
        return players_serializer.data
    
    def get_channel_role(self, obj):
        return str(obj.channel_role)
    
    def get_channel_id(self, obj):
        return str(obj.channel_id)


class QuestionListSerializer(ModelSerializer):
    last_owner = serializers.CharField()
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
    def get_last_owner(self, obj):
        return str(obj.last_owner.channel_role)

class QuestionRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Question
        exclude = [
            "answer_text",
            "answer_file",
        ]



class ContractListSerializer(ModelSerializer):
    first_party_team = serializers.CharField()
    second_party_team = serializers.CharField()
    first_party_player = serializers.CharField()
    second_party_player = serializers.CharField()
    class Meta:
        model = Contract
        fields = [
            "id",
            "contract_type",
            "first_party_team",
            "second_party_team",
            "first_party_player",
            "second_party_player",
            "contract_type",
            "cost",
            "terms",
            "first_party_agree",
            "second_party_agree",
            "is_rejected",
        ]
    def get_first_party_team(self, obj):
        return str(obj.first_party_team.channel_role)
    def get_second_party_team(self, obj):
        return str(obj.second_party_team.channel_role)
    def get_first_party_player(self, obj):
        return str(obj.first_party_player.discord_id)
    def get_second_party_player(self, obj):
        return str(obj.second_party_player.discord_id)
    

class ContractRetrieveSerializer(ModelSerializer):
    first_party_team = serializers.CharField()
    second_party_team = serializers.CharField()
    first_party_player = serializers.CharField()
    second_party_player = serializers.CharField()
    class Meta:
        model = Contract
        fields = "__all__"
    def get_first_party_team(self, obj):
        return str(obj.first_party_team.channel_role)
    def get_second_party_team(self, obj):
        return str(obj.second_party_team.channel_role)
    def get_first_party_player(self, obj):
        return str(obj.first_party_player.discord_id)
    def get_second_party_player(self, obj):
        return str(obj.second_party_player.discord_id)


class PlayerListSerializer(ModelSerializer):
    roles = serializers.SerializerMethodField()
    discord_id = serializers.CharField()
    team = serializers.CharField()
    class Meta:
        model = Player
        fields = [
            "first_name",
            "last_name",
            "discord_username",
            "discord_id",
            "team",
            "status",
            "roles"
        ]
    def get_roles(self, obj):
        roles = obj.player_role.all()
        roles = list(map(lambda role: role.pk, roles))

        return roles
    
    def get_discord_id(self, obj):
        return str(obj.discord_id)

    def get_team(self, obj):
        return str(obj.team.channel_role)

class PlayerRetrieveSerializer(ModelSerializer):
    discord_id = serializers.CharField()
    team = serializers.CharField()
    class Meta:
        model = Player
        fields = "__all__"

    def get_discord_id(self, obj):
        return str(obj.discord_id)

    def get_team(self, obj):
        return str(obj.team.channel_role)


class WarehouseBoxListSerializer(
    ModelSerializer
    ):

    class Meta:
        model = WarehouseBox
        fields = "id", "is_lock", "level", "lock_state"

class WarehouseQuestionSerializer(
    ModelSerializer
    ):
    class Meta:
        model   = WarehouseQuestions
        fields  = "id", "text", "attachment"

class WarehouseBoxRetrieveSerializer(
    ModelSerializer
    ):
    lock_question = WarehouseQuestionSerializer()
    class Meta:
        model   = WarehouseBox
        fields  = (
            "id",
            "lock_state",
            "is_lock",
            "lock_question",
            "level",
            "money"
        )

class WarehouseQuestionListSerializer(
    ModelSerializer
):
    class Meta:
        model = WarehouseQuestions
        fields = "id", "text"

class WarehouseQuestionRetrieveSerializer(
    ModelSerializer
):
    class Meta:
        model = WarehouseQuestions
        fields = "id", "text", "attachment"


class TeamQuestionRelRetrieveSerializer(
    ModelSerializer
):
    class Meta:
        model = TeamQuestionRel
        fields = "__all__"

class TeamQuestionRelListSerializer(
    ModelSerializer
):
    class Meta:
        model = TeamQuestionRel
        fields = "id", "team", "question", "solved"



class ConfSerializer(
    ModelSerializer
):
    class Meta:
        model = ConstantConfig
        fields = "state",