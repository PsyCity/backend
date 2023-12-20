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
router.register(prefix="players",
                viewset=views.PlayerViewSet,
                basename="players"
                )
router.register(prefix="warehouse_boxes",
                viewset=views.WarehouseViewSet
                )

urlpatterns = [
    path("", include(router.urls))
]
