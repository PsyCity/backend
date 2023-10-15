from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import member, action

member_router = DefaultRouter()
member_router.register("role", member.RoleViewset, "role")
member_router.register("kick", member.KickViewset, "kick")
member_router.register("invite", member.InviteViewset, "invite")
app_name = "team_api"

action_router = DefaultRouter()
action_router.register("kill-homeless", action.KillHomelessViewSet, "kill_homeless")
action_router.register("depositbox-sensor-report", action.DepositBoxSensor, "depositbox_sensor_report")

urlpatterns = [
    path("member/", include(member_router.urls)),
    path("action/", include(action_router.urls))
]