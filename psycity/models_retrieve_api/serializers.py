from core.serializers import TeamSerializer

class TeamListSerializer(TeamSerializer):
    class Meta(TeamSerializer.Meta):
        fields = [
            "id",
            "name",
            "state"
        ]

class TeamRetrieveSerializer(TeamSerializer):
    class Meta(TeamSerializer.Meta):
        fields = "__all__"