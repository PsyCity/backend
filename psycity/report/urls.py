
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from . import views 

router = DefaultRouter()
router.register(
    "simple_report",
    views.SimpleReportViewSet,
)
router.register(
    "contract_report",
    views.ContractReportViewSet
)
urlpatterns = [
    path("", include(router.urls))
]
