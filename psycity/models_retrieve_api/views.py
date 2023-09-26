from rest_framework.viewsets import GenericViewSet, mixins

from core.models import (
    Team
)

from models_retrieve_api.serializers import *
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
    