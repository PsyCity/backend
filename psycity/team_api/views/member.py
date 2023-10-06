from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.exceptions import ValidationError, NotAcceptable


from core.models import Player, PlayerRole, TeamJoinRequest
from core.config import TEAM_MEMBER_MIN
from team_api import serializers, schema
from rest_framework.response import Response
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

    def perform_update(self, serializer:serializers.TeamMemberSerializer, instance):
        player = instance
        validated_data = serializer.validated_data
        team = player.team
        if not team:
            raise ValidationError("team does not exist")


        role = validated_data.get("role")
        if not role:
            raise ValidationError("role cant be null",400)
        role = PlayerRole.objects.get(name=role)

        serializer.update(
            instance=instance,
            validated_data=validated_data
        )
    
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
        if (n_of_player:=team.player_team.count()) <= TEAM_MEMBER_MIN:
            raise NotAcceptable("Team members are not enough", 406)
        agreement = serializer.validated_data.get("agreement")
        if agreement < (n_of_player - 1):
            raise NotAcceptable("Not enough vote.", 406) 
        player.team = None
        player.status = Player.STATUS_CHOICES[1][0]
        player.player_role.clear()
        player.save()


class InviteViewset(mixins.CreateModelMixin,mixins.ListModelMixin,
                    GenericViewSet):
    serializer_class = serializers.TeamJoinRequestSerializer
    queryset = TeamJoinRequest.objects.all()
    http_method_names = ["post", "get"]

    @schema.invite_schema
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.TeamJoinRequestSerializer(queryset, many=True)
        return Response(serializer.data)

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