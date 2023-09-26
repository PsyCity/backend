from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from core.models import (
    Team,
    Question
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
        return obj.name

class QuestionListSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "pk",
            "title"
        ]

class QuestionRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Question
        exclude = [
            "answer"
        ]