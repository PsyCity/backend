from django.urls import path
from . import views


urlpatterns = [
    path('team/leave/', views.PlayerLeftTeam.as_view()),
    path('team/join/', views.PlayerJoinTeam.as_view()),
]