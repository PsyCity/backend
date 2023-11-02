from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import member, action, contract, money

member_router = DefaultRouter()
member_router.register("role", member.RoleViewset, "role")
member_router.register("kick", member.KickViewset, "kick")
member_router.register("invite", member.InviteViewset, "invite")
app_name = "team_api"

action_router = DefaultRouter()
action_router.register("kill-homeless", action.KillHomelessViewSet, "kill_homeless")
action_router.register("depositbox-sensor-report", action.DepositBoxSensor, "depositbox_sensor_report")
action_router.register("discover_bank_robber", action.DiscoverBankRobber)

contract_router = DefaultRouter()
contract_router.register("register", contract.Register, "contract")
contract_router.register("approvement", contract.Approvement, "contract")
contract_router.register("pay", contract.Pay, "contract")

money_router = DefaultRouter()
money_router.register("exchenge", money.TeamMoneyViewSet, "money")

urlpatterns = [
    path("member/", include(member_router.urls)),
    path("action/", include(action_router.urls)),
    path("contract/", include(contract_router.urls)),
    path("money/", include(money_router.urls)),
]
