from rest_framework.viewsets import GenericViewSet, mixins

from core.models import (
    Team,
    Question,
    Contract
)

from models_retrieve_api.serializers import (
    TeamListSerializer,
    TeamRetrieveSerializer,

    QuestionListSerializer,
    QuestionRetrieveSerializer,

    ContractListSerializer,
    ContractRetrieveSerializer
)
# Create your views here.

class TeamViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
    ):
    queryset = Team.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TeamRetrieveSerializer
        return TeamListSerializer
    

class QuestionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
    ):
    queryset= Question.objects.filter(is_published=True).all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return QuestionRetrieveSerializer
        return QuestionListSerializer
    
class ContractViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
    ):
    queryset= Contract.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ContractListSerializer
        return ContractRetrieveSerializer
    
    