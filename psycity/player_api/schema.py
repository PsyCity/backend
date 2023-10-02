from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


left_team_schema = swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "player_id" : openapi.Schema(
                type=openapi.TYPE_INTEGER
            )
        }
    )
)