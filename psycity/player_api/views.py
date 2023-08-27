from django.shortcuts import render

from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.response import Response
from rest_framework.exceptions import APIException, bad_request

from .serializers import TeamJoinRequestSerializer, PlayerSerializer
from core.models import TeamJoinRequest, Team
# Create your views here.

RESPONSE_BASE = {
    "data" : [],
    "status_code": 200,
    "message" : "",
    "result" : ""
}

class JoinViewset(  mixins.UpdateModelMixin,
                    mixins.RetrieveModelMixin,
                    GenericViewSet):
    
    serializer_class = TeamJoinRequestSerializer
    queryset = TeamJoinRequest.objects.all()
    http_method_names=["get", "patch", "options"]

    def partial_update(self, request, *args, **kwargs):
        self.error = None
        super().partial_update(request, *args, **kwargs)
        content = RESPONSE_BASE
        return Response(content)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        content = RESPONSE_BASE
        content["data"] = response.data
        return Response(content)



    # def partial_update(self, request, *args, **kwargs):
    #     response = super().partial_update(request, *args, **kwargs)
    #     content = RESPONSE_BASE
    #     content["message"] = "player joined the team"
    #     return Response(content)

    # def perform_update(self, serializer: TeamJoinRequestSerializer):
    #     if serializer.data["state"] == "active":
    #         join_request = serializer.instance
    #         serializer.is_valid(raise_exception=True)
    #         player = join_request.player_id
    #         player.status = "TeamMember"
    #         team = Team.objects.get(pk=serializer.data.get("team_id"))
    #         player.team_id = team
    #         join_request.state="inactive"
    #         player.save()
    #         print()
    #         join_request.save()
    
class JoinListViewset(mixins.ListModelMixin,
                      GenericViewSet):
    serializer_class = TeamJoinRequestSerializer
    queryset = TeamJoinRequest.objects.all()

    def get_queryset(self):
        player_id = self.request.query_params.get("player_id")
        return super().get_queryset().filter(player_id=player_id)

    

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        content = RESPONSE_BASE
        content["data"] = response.data["results"]
        return Response(content)