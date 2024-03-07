from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import member, action, contract, money, loan, question

member_router = DefaultRouter()
member_router.register("role", member.RoleViewset, "role")
member_router.register("kick", member.KickViewset, "kick")
member_router.register("invite", member.InviteViewset, "invite")
app_name = "team_api"

action_router = DefaultRouter()
action_router.register("kill-homeless", action.KillHomelessViewSet, "kill_homeless")
action_router.register("depositbox-sensor-report", action.DepositBoxSensor, "depositbox_sensor_report")
# action_router.register("discover_bank_robber", action.DiscoverBankRobber)
# action_router.register("bank_robbery_way", action.BankRobberyWayViewSet, "bank_robbery_way")
# action_router.register("bank_robbery", action.BankRobberyViewSet, "bank_robbery")
# action_router.register("bank_sensor_installation", action.BankSensorInstallViewSet, "bank_sensor_installation")
# action_router.register("warehouse", action.WarehouseDepositBoxRobberyViewSet, "warehouse_robbery")
# action_router.register("bank-sensor-install-way", action.BankSensorInstallWay, "Bank_sensor_install")
action_router.register("mafia_warehouse_robbery", action.WarehouseDepositBoxRobberyViewSet, "warehouse_robbery")
action_router.register("police_warehouse_hack", action.WarehouseDepositBoxHackViewSet, "warehouse_hack")
action_router.register("citizen_warehouse_hack_check", action.WarehouseDepositBoxHackCheckViewSet, "warehouse_hack_check")
action_router.register("find_card", action.FindCardViewSet, "Team_card")

contract_router = DefaultRouter()
contract_router.register("register", contract.Register, "contract")
contract_router.register("sign", contract.Sign, "contract")
contract_router.register("pay", contract.Pay, "contract")
contract_router.register("confirm", contract.Confirm, "contract")

money_router = DefaultRouter()
money_router.register("exchenge", money.TeamMoneyViewSet, "money")
money_router.register("property", money.PropertyViewSet, "property")

loan_router = DefaultRouter()
loan_router.register("receive", loan.Receive, "loan")
loan_router.register("repayment", loan.Repay, "loan")

urlpatterns = [
    path("member/", include(member_router.urls)),
    path("action/", include(action_router.urls)),
    path("contract/", include(contract_router.urls)),
    path("money/", include(money_router.urls)),
    path("question/buy/", question.QuestionBuyView.as_view(), name="team_question_buy"),
    path('question/list/<int:team_id>/', question.TeamQuestions.as_view(), name='team_questions'),
    path('question/solve/', question.QuestionSolveView.as_view(), name='question-solve'),
    path('question/update/', question.UpdateQuestionPrice.as_view({"get": "list"}), name='question-update'),
    path('contract/list/<int:team_id>/', contract.TeamContracts.as_view(), name='team_contracts'),
    path('contract/reject/', contract.Reject.as_view(), name='contract_reject'),
    path("loan/", include(loan_router.urls)),
]