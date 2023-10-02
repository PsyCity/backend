from django.urls import path
from . import views


urlpatterns = [
    path("id_by_discord/", views.PlayerIdByDiscord.as_view(), name="discord_player_id")
]