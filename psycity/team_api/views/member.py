from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.exceptions import ValidationError

from core.models import Player, PlayerRole

from team_api import serializers
from team_api.utils import ResponseStructure

# Create your views here.


class MemberRoleViewset(mixins.UpdateModelMixin,
                        GenericViewSet):
    serializer_class = serializers.TeamMemberSerializers
    queryset = Player.objects.all()


    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer, instance)
        return ResponseStructure().response

    def perform_update(self, serializer, instance):
        player = instance
        
        team = player.team
        if not team:
            raise ValidationError("team does not exist")

        role = serializer.validated_data.get("role")
        if not role:
            raise ValidationError("role cant be null",400)
        role = PlayerRole.objects.get(name=role)

        todo = serializer.validated_data.get("todo")
        if todo == "add":
            players = team.player_team.all()
            players = list(filter(lambda p: role in p.player_role.all(), players))
            map(lambda p: p.player_role.remove(role),players)

            player.player_role.add(role)

        elif todo=="delete":
            player.player_role.remove(role)

    