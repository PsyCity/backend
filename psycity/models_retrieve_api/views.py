from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.response import Response

from core.models import (
    Team,
    Question,
    Contract,
    Player
)

from models_retrieve_api.serializers import (
    TeamListSerializer,
    TeamRetrieveSerializer,

    QuestionListSerializer,
    QuestionRetrieveSerializer,

    ContractListSerializer,
    ContractRetrieveSerializer,

    PlayerListSerializer,
    PlayerRetrieveSerializer,
)


class ListModelMixin:
    """
    List a queryset.
    """
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# Create your views here.

class TeamViewSet(
    ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
    ):
    queryset = Team.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TeamRetrieveSerializer
        return TeamListSerializer
    

class QuestionViewSet(
    ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
    ):
    queryset= Question.objects.filter(is_published=True).all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return QuestionRetrieveSerializer
        return QuestionListSerializer
    
class ContractViewSet(
    ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
    ):
    queryset= Contract.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ContractListSerializer
        return ContractRetrieveSerializer
    
class PlayerViewSet(
    ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
    ):
    queryset= Player.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return PlayerListSerializer
        return PlayerRetrieveSerializer