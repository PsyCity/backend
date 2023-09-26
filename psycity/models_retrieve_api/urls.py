from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views


app_name = "models_retrieve_api"

router = DefaultRouter()
router.register("teams", views.TeamViewSet)

urlpatterns = [
    path("", include(router.urls))
]
