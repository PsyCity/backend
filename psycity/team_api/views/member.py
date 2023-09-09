from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.exceptions import ValidationError, NotAcceptable


from core.models import Player, PlayerRole, TeamJoinRequest

from team_api import serializers, schema
from team_api.utils import ResponseStructure

# Create your views here.


class RoleViewset(mixins.UpdateModelMixin,
                        GenericViewSet):
    serializer_class = serializers.TeamMemberSerializer
    queryset = Player.objects.all()
    http_method_names = ["patch"]

    @schema.role_schema
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

    
class KickViewset(mixins.UpdateModelMixin,
                  GenericViewSet):
    serializer_class = serializers.TeamMemberSerializer
    queryset = Player.objects.all()
    http_method_names = ["patch"]

    @schema.kick_schema
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer, instance)
        return ResponseStructure().response
    
    def perform_update(self, serializer, player):
        team = player.team
        if not team:
            raise ValidationError("no team for player")
        if (n_of_player:=team.player_team.count()) <= 2:
            raise ValidationError("Team members are not enough")
        agreement = serializer.validated_data.get("agreement")
        if agreement < (n_of_player - 1):
            raise ValidationError("Not enough vote.") 
        player.team = None
        player.status = Player.STATUS_CHOICES[1]
        player.player_role.clear()
        player.save()


class InviteViewset(mixins.CreateModelMixin,
                    GenericViewSet):
    serializer_class = serializers.TeamJoinRequestSerializer
    queryset = TeamJoinRequest.objects.all()
    http_method_names = ["post"]

    @schema.invite_schema
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        
        join_request = \
            TeamJoinRequest.objects.filter(
                player = serializer.validated_data.get("player"),
                team = serializer.validated_data.get("team"),
                state = "active"
            ).first()
        
        if join_request:
            raise NotAcceptable("an active request exist")   
            
        serializer.save(state='active')