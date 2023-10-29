from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions
from django.http import Http404
from rest_framework.decorators import action

from core.models import Team, Contract 
from team_api.serializers import ContractRegisterSerializer, ContractApprovementSerializer
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
        except exceptions.NotAcceptable as e:
            return Response(
                data={
                    "message": "Not Acceptable error.",
                    "data": [e.detail],
                    "result": None
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
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
    
class Approvement(
    GenericViewSet,
    mixins.UpdateModelMixin
    ):
    http_method_names = ["patch"]

    serializer_class = ContractApprovementSerializer
    
    queryset = Contract.objects.filter(
        first_party_agree=True, 
        second_party_agree=False,
        state=1
        )

    def partial_update(self, request, *args, **kwargs):
        
        try:
            super().partial_update(request, *args, **kwargs)
            return Response(
                data={
                    "message": "signed successfully.",
                    "data": [],
                    "result": None
                },
                status=status.HTTP_200_OK
            )
        
        except Http404:
            return Response(
                data={
                    "message": "Valid contract not found.",
                    "data": [],
                    "result":None
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        except exceptions.ValidationError as e:
            return Response(
                data={
                    "message" : "Validation error",
                    "data": [e.detail],
                    "result" : None
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except exceptions.NotAcceptable as e:
            return Response(
                data={
                    "message": "Not Acceptable error.",
                    "data": [e.detail],
                    "result": None
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        # except exceptions
        except Exception as e:
            return Response(
                data={
                    "message": "Something went wrong.",
                    "data": [],
                    "result": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def perform_update(self, serializer):
        serializer.save(
            second_party_agree=True,
            state=2
        )
        