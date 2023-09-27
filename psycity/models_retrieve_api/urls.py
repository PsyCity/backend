from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views


app_name = "models_retrieve_api"

router = DefaultRouter()
router.register("teams",
                views.TeamViewSet
                )
router.register(prefix="questions",
                viewset=views.QuestionViewSet,
                basename="questions"
                )
router.register(prefix="contracts",
                viewset=views.ContractViewSet
                )

urlpatterns = [
    path("", include(router.urls))
]
