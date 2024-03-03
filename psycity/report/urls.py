
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from . import views 

router = DefaultRouter()
router.register(
    "simple_report",
    views.SimpleReportViewSet,
)

urlpatterns = [
    path("", include(router.urls))
]
