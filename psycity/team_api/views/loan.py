from rest_framework.viewsets import (
    GenericViewSet,
    mixins
)
from rest_framework.response import Response
from rest_framework import status
from core.models import Team
from team_api.serializers import LoanSerializer
from team_api.utils import response

class Receive(
    GenericViewSet,
    mixins.UpdateModelMixin
    ):

    serializer_class = LoanSerializer
    queryset = Team.objects.all()

    @response
    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            data={
                "message":"Loan request accepted.",
                "data": [],
                "result": None
            },
            status=status.HTTP_200_OK
        )
    
    def perform_update(self, serializer):
        serializer.save() #update time + pay there money