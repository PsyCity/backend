from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.response import Response
from rest_framework import status
from core.models import Report, Team
from core.config import HIDDEN_ID_LEN
from team_api.utils import response
from .serializers import SimpleReportSerializer, ContractReportSerializer
# Create your views here.

class SimpleReportViewSet(
    GenericViewSet,
    mixins.CreateModelMixin
    ):
    
    serializer_class = SimpleReportSerializer
    queryset = Report.objects.all()
    
    @response
    def create(self, request, *args, **kwargs):
        r = super().create(request, *args, **kwargs)
        return Response(
            data={
                "message": "Reported.",
                "data": [],
                "result": r.data.get("id"),
            },
            status=status.HTTP_200_OK,
        )

    def perform_create(self,
                       serializer: SimpleReportSerializer
                       ):
        # LOG NEW REPORT
        return super().perform_create(serializer)
    
class ContractReportViewSet(
    GenericViewSet,
    mixins.CreateModelMixin
    ):
    
    serializer_class = ContractReportSerializer
    queryset = Report.objects.all()
    team_query_set = Team.objects.all()
 
    @response
    def create(self, request, *args, **kwargs):
        if request.data.get('team_reporter'):
            if len(str(request.data.get('team_reporter'))) == HIDDEN_ID_LEN:
                team = self.team_query_set.filter(hidden_id=request.data.get('team_reporter'))
                if not team:
                    return Response(
                     data={
                        "message": "team_reporter not found.",
                        "data": [],
                        "result": None,
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
                request.data['team_reporter'] = team.first().channel_role

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.is_acceptable()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            data={
                "message": "Reported.",
                "data": [],
                "result": serializer.data.get("id"),
            },
            status=status.HTTP_200_OK,
            headers=headers
        )
        
    
    def perform_create(self, serializer):
        serializer.save(
            report_type=2,
        )