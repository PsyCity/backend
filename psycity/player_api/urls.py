from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

loan_router = DefaultRouter()
loan_router.register(prefix="receive", 
                     viewset=views.LoanReceive,
                     basename="loan"
                     )

urlpatterns = [
    path('team/leave/', views.PlayerLeftTeam.as_view()),
    path('team/join/', views.PlayerJoinTeam.as_view()),
    path("id_by_discord/", views.PlayerIdByDiscord.as_view(), name="discord_player_id"),
    path("loan/", include(loan_router.urls)),
]