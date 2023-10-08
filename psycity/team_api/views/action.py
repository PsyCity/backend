from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import status
from team_api.serializers import KillHomelessSerializer
from core.models import Player
from team_api.utils import transfer_money



class KillHomelessViewSet(GenericViewSet):

    serializer_class = KillHomelessSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data, code = self.perform_kill(serializer)
            return Response(
                data=data,
                status=code
            )
        except Player.DoesNotExist:
            pass

    def perform_kill(self, serializer):
        team = serializer.validated_data.get("team_id")
        player = serializer.validated_data.get("homeless_id")
        if bodyguard:=self.bodyguard_exist(player):
            if team.level > bodyguard.level:
                """
                decrease contract_amount + penaly_percent from police
                add contract_amount + bonus to bodyguard 
                kill homeless
                """
                # self.kill(player)
                ...
            elif team.level == bodyguard.level:
                """
                transfer 1/2 * contract_cost to mafia
                """
                ...
            elif team.level < bodyguard.level:
                """
                transfer from mafia to bodyguard 
                """
                ...

        self.kill(player)
        # TODO : archive contract
        data={
            "message": "homeless killed successfully.",
            "data" :[],
            "result" : None
        }

        return data, status.HTTP_200_OK
    
    def kill(self, player):
        ...

    def bodyguard_exist(self, player):
        ...