from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import member

member_router = DefaultRouter()
member_router.register("role", member.RoleViewset, "role")

app_name = "team_api"

urlpatterns = [
    path("member/", include(member_router.urls))
]