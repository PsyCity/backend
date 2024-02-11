from django.utils import timezone

from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework import exceptions
from rest_framework.response import Response

from abc import ABC, abstractmethod

from core.models import Team
from team_api.utils import ListModelMixin, response
from team_api.schema import bank_robbery_list_schema


class BankPenetrationBaseViewSet(ABC,
                                 GenericViewSet,
                                 ListModelMixin
                                 ):
    team_role_allowed = "Mafia"
    success_message_list = ""
    success_message_deposit = ""

    @abstractmethod
    def get_serializer_class(self):
        ...

    @bank_robbery_list_schema
    @response
    def list(self, request, *args, **kwargs):
        owner = request.GET["team_id"]
        if not owner:
            raise exceptions.ValidationError("Set team_id in url params.")

        self.__validate_owner(owner)
        queryset = self.query(owner)
        serializers = self.get_serializer(queryset, many=True)
        return Response(
            data={
                "message": self.success_message_list,
                "data": serializers.data,
                "result": None,
            }
        )
        
    @abstractmethod
    def query(self, owner):
        ...

    def __validate_owner(self, owner_pk):
        assert self.team_role_allowed is not None,\
        "set team_role_allowed"

        try:
            team = Team.objects.get(pk=owner_pk)
        except:
            raise exceptions.NotFound("team not found")

        if team.team_role != self.team_role_allowed:
            raise exceptions.NotAcceptable(f"Not {self.team_role_allowed}.")


    @action(
            methods=["patch"],
            detail=True
            )
    @response
    def open_escape_room(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
            )

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            data={
                "message": "good luck.",
                "data": [],
                "result": None
                },
            )

    def perform_update(self, serializer):
        serializer.save(
            state=2,
            opening_time=timezone.now()
            )


    @action(
        methods=["POST"],
        detail=True,
        url_path="deposit_box"
        )
    @response
    def open_deposit_box(self, request, bpk=None, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.is_acceptable()
        self.perform_on_box(serializer)
        return Response(
            data={
                "message": f"{self.success_message_deposit} successfully.",
                "data": [],
                "result": None}
        )

    @abstractmethod
    def perform_on_box(self, serializer): 
        ...

    def notify(self):
        # LOGGER
        # Client_API

        print("Client API is not implemented!!") 
