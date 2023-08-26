from django.urls import path
from . import views

app_name = "team_api"

urlpatterns = [
    path("member/role/", views.MembersRole.as_view(), name="member-role")    
]