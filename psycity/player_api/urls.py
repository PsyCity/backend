from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("property",
                viewset=views.PropertyViewSet)

urlpatterns = [
    path('team/leave/', views.PlayerLeftTeam.as_view()),
    path('team/join/', views.PlayerJoinTeam.as_view()),
    path("id_by_discord/", views.PlayerIdByDiscord.as_view(), name="discord_player_id"),
    path("loan/receive", views.LoanReceive.as_view(), name="loan-receive"),
    path('loan/repayment', views.PlayerLoanRepayment.as_view(), name='player_loan_repayment'),
    path("bodyguard/request/", views.BodyguardViewSet.as_view({"post":"create"}), name="player_bodyguard_request"),
    path("bodyguard/approvement/<int:pk>/", views.BodyguardViewSet.as_view({"patch": "partial_update"}), name="player_bodyguard_approvement"),
    path("login", views.Login.as_view(), name="login"),
    path('contract/list/<int:player_id>/', views.PlayerContracts.as_view(), name='player_contracts'),
    path("", include(router.urls)),
]