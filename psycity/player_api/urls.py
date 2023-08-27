from django.urls import path, include
from . import views
from rest_framework import routers

player_team_router = routers.SimpleRouter()
player_team_router.register("join", views.JoinViewset, basename="join")
player_team_router.register("join-requests", views.JoinListViewset, basename="join")

app_name = "player_api"

urlpatterns = [
    path("team/", include(player_team_router.urls))
    
]