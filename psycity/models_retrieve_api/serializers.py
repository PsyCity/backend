from rest_framework.serializers import ModelSerializer

from core.models import Question
class TeamListSerializer:
    class Meta:
        fields = [
            "id",
            "name",
            "state"
        ]

class TeamRetrieveSerializer:
    class Meta:
        fields = "__all__"



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