from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.response import Response
from rest_framework import status
from core.models import Report
from team_api.utils import response
from .serializers import SimpleReportSerializer
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