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
    channel_role = serializers.SerializerMethodField()
    channel_id = serializers.SerializerMethodField()
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
    discord_id = serializers.SerializerMethodField()

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
    channel_role = serializers.SerializerMethodField()
    channel_id = serializers.SerializerMethodField()
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
    last_owner = serializers.SerializerMethodField()
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
        if obj.last_owner:
            return str(obj.last_owner.channel_role)
        return None

class QuestionRetrieveSerializer(ModelSerializer):
    attachment = serializers.SerializerMethodField()
    class Meta:
        model = Question
        exclude = [
            "answer_text",
            "answer_file",
        ]

    def get_attachment(self, obj):
        request = self.context.get('request')
        if obj.attachment:
            if request:
                base_url = request.build_absolute_uri('/')[:-1]
                attachment_url = str(obj.attachment) if obj.attachment else str(obj.attachment_link or '')
                return f"{base_url}/{attachment_url}"
            else:
                return str(obj.attachmen.url)
        elif obj.attachment_link:
            return str(obj.attachment_link)
        else:
            return str('')


class ContractListSerializer(ModelSerializer):
    first_party_team = serializers.SerializerMethodField()
    second_party_team = serializers.SerializerMethodField()
    first_party_player = serializers.SerializerMethodField()
    second_party_player = serializers.SerializerMethodField()
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
        if obj.first_party_team:
            return str(obj.first_party_team.channel_role)
        return None
    def get_second_party_team(self, obj):
        if obj.second_party_team:
            return str(obj.second_party_team.channel_role)
        return None
    def get_first_party_player(self, obj):
        if obj.first_party_player:
            return str(obj.first_party_player.discord_id)
        return None
    def get_second_party_player(self, obj):
        if obj.second_party_player:
            return str(obj.second_party_player.discord_id)
        return None
    

class ContractRetrieveSerializer(ModelSerializer):
    first_party_team = serializers.SerializerMethodField()
    second_party_team = serializers.SerializerMethodField()
    first_party_player = serializers.SerializerMethodField()
    second_party_player = serializers.SerializerMethodField()
    class Meta:
        model = Contract
        fields = "__all__"

    def get_first_party_team(self, obj):
        if obj.first_party_team:
            return str(obj.first_party_team.channel_role)
        return None
    def get_second_party_team(self, obj):
        if obj.second_party_team:
            return str(obj.second_party_team.channel_role)
        return None
    def get_first_party_player(self, obj):
        if obj.first_party_player:
            return str(obj.first_party_player.discord_id)
        return None
    def get_second_party_player(self, obj):
        if obj.second_party_player:
            return str(obj.second_party_player.discord_id)
        return None

class PlayerListSerializer(ModelSerializer):
    roles = serializers.SerializerMethodField()
    discord_id = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
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
        if obj.team:
            return str(obj.team.channel_role)
        return None

class PlayerRetrieveSerializer(ModelSerializer):
    discord_id = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
    class Meta:
        model = Player
        fields = "__all__"

    def get_discord_id(self, obj):
        return str(obj.discord_id)

    def get_team(self, obj):
        if obj.team:
            return str(obj.team.channel_role)
        return None


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
    attachment = serializers.SerializerMethodField()
    class Meta:
        model = WarehouseQuestions
        fields = "id", "text", "attachment"
    
    def get_attachment(self, obj):
        request = self.context.get('request')
        if obj.attachment:
            if request:
                base_url = request.build_absolute_uri('/')[:-1]
                attachment_url = str(obj.attachment) if obj.attachment else str(obj.attachment_link or '')
                return f"{base_url}/{attachment_url}"
            else:
                return str(obj.attachmen.url)
        elif obj.attachment_link:
            return str(obj.attachment_link)
        else:
            return str('')


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