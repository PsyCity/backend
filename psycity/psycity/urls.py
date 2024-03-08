"""
URL configuration for psycity project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path

from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from core import views as core_views


schema_view = get_schema_view(
   openapi.Info(
      title="PSYCITY API",
      default_version='v1',
      description="API Document for pcycity",
   ),
   public=True,
   permission_classes=(AllowAny,),
)


urlpatterns = [
    path('admin/leaderboard/', core_views.leaderboard_secret, name='leaderboard'),

    path('admin/', admin.site.urls),
    path('data_dir/<str:filedir>/<str:filename>', core_views.data_dir_api, name='data_dir_api'),
    path('api/v1/player/', include('player_api.urls')),
    path('api/v1/team/', include('team_api.urls')),
    path('api/v1/models/', include('models_retrieve_api.urls')),
    path('api/v1/reports/', include('report.urls')),

    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('leaderboard/', core_views.leaderboard, name='leaderboard'),
]
