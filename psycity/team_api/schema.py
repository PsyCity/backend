from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import ResponseStructure
from . import serializers



agreement_schema = \
    openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "player_id" : openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                ),
                "is_agree" : openapi.Schema(
                    type=openapi.TYPE_BOOLEAN
                )
            }
            
            )
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
