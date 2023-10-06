from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import Serializer
from team_api.serializers import TeamMoneyTransferSerializer

class TeamMoneyTransfer(ModelViewSet):
    http_method_names = ["post"]
    
    serializer_class = TeamMoneyTransferSerializer
    
    def perform_update(self, serializer):
        instance = self.get_object()
        pass