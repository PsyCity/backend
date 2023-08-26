from django.shortcuts import render
from rest_framework.generics import  GenericAPIView
from . import serializers
from .utils import ResponseStructure
# Create your views here.

class MembersRole(GenericAPIView):
    serializer_class = serializers.TeamMemberSerializers

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)   #TODO: handel exceptions
        team = serializer.team
        serializer.update(team, serializer.validated_data)
        response = ResponseStructure()  #TODO: remove data from response 200
        return response.response
    