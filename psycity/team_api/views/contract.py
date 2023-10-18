from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions

from core.models import Team 
from team_api.serializers import ContractRegisterSerializer
class Register(
    GenericViewSet,
    mixins.CreateModelMixin
    ):

    serializer_class = ContractRegisterSerializer

    def create(self, request, *args, **kwargs):
        try:
            r = super().create(request, *args, **kwargs)
            return Response(
                data={
                    "message": "Contract created successfully.",
                    "data": [],
                    "result": r.data.get("id")
                },
                status=status.HTTP_201_CREATED
            )
        
        except exceptions.ValidationError as e:
            return Response(
                data={
                    "message": "Validation error.",
                    "data": e.detail,
                    "result": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                data={
                    "message": "Something went wrong.",
                    "data" : [],
                    "result": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        serializer.save(
            first_party_agree=True,
            second_party_agree=False,
            archive=False,
            state=1
        )
    