from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.response import Response
from rest_framework import exceptions, status
from rest_framework.generics import RetrieveAPIView

from core.models import (
    Team,
    Question,
    Contract,
    WarehouseBox,
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

    WarehouseBoxListSerializer,
    WarehouseBoxRetrieveSerializer
)

from team_api.utils import response

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
        
    
    def get_object(self):
        lookup_value = self.kwargs.get('pk')
        lookup_value_int = int(lookup_value)

        if len(lookup_value) == 10:
            self.kwargs['pk'] = self.queryset.filter(hidden_id=lookup_value_int).first().channel_role

        return super().get_object()
    

    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return Response(serializer.data)
        except Team.DoesNotExist:
            return Response({'detail': 'Team not found'}, status=status.HTTP_404_NOT_FOUND)


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
    
class WarehouseViewSet(
    ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = WarehouseBox.objects.all()
    
    def get_serializer_class(self):
        if self.action == "list":
            return WarehouseBoxListSerializer
        
        elif self.action == "retrieve":
            return WarehouseBoxRetrieveSerializer
        else:
            raise exceptions.MethodNotAllowed(
                "server side error"
                )

    def get_queryset(self):
        if self.action == "list":
            return self.queryset
        elif self.action == "retrieve":
            return self.queryset.select_related()
        return super().get_queryset()

    @response
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @response    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
