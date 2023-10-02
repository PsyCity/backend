from django.urls import path
from . import views


urlpatterns = [
    path('team/leave/', views.PlayerLeftTeam.as_view()),
    path('team/join/', views.PlayerJoinTeam.as_view()),
    path("id_by_discord/", views.PlayerIdByDiscord.as_view(), name="discord_player_id"),
    path("loan/receive", views.LoanReceive.as_view(), name="loan-receive"),
    path('loan/repayment', views.PlayerLoanRepayment.as_view(), name='player_loan_repayment'),
]