from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import member
from .views import money

app_name = "team_api"

urlpatterns = [
    path("member/role", member.RoleViewset.as_view({"patch": "partial_update"}), name='team_member_role'),
    path("member/kick", member.KickViewset.as_view({"patch": "partial_update"}), name='team_member_kick'),
    path("member/invite", member.InviteViewset.as_view({"post": "create", "get": "list"}), name='team_member_invite'),
    path("money/transfer", money.TeamMoneyTransfer.as_view({"post": "perform_update"}), name='team_money_transfer'),
]