from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import ResponseStructure
from . import serializers



agreement_schema = \
    openapi.Schema(
        type=openapi.TYPE_INTEGER,
        )


role_schema = swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "agreement" : agreement_schema,
        }
    ),
    responses={
        200: ResponseStructure().schema,
    },
)


kick_schema = swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "agreement" : agreement_schema
        }
    ),
    responses={
        200 : ResponseStructure().schema
    }
)

invite_schema = swagger_auto_schema(
    operation_description="invite a player to Team",
    responses={
        201: ResponseStructure(status_code=201).schema
    }
)


deposit_list_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            "sensor_owner_pk",
            openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER
        )
    ]
)

invite_list_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            "player_pk",
            openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER
        )
    ]
)

bank_robbery_list_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            "team_id",
            openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER
        )
    ]
)