from typing import Any
from rest_framework.response import Response

from drf_yasg import openapi


class ResponseStructure:
    def __init__(self,
                result="",
                data=[],
                error_msg="",
                status_code=200) -> None:
        
        self.result = result
        self._data=data
        self.error_msg = error_msg
        self.code = status_code

    @property
    def data(self):
        return {
            "result" : self.result,
            "data" : self._data,
            "error_message" : self.error_msg,
            "status_code": self.code
        }
    @property
    def response(self):
        return Response(self.data)

    @property
    def schema(self):
        schema = \
            openapi.Response(
                description="OK",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "result" : openapi.Schema(
                            type = openapi.TYPE_STRING,
                            pattern=self.result
                        ),
                        "data" : openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items= openapi.Schema( type=openapi.TYPE_STRING),
                            default=self._data
                        ),
                        "error_msg" : openapi.Schema(
                            type=openapi.TYPE_STRING,
                        ),
                        "status_code" : openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            default=self.code
                        ),
                    }
                )
            )
        return schema
    

def transfer_money(from_team,
                   penalty_percent,
                   to_team,
                   bonus_percent,
                   amount
                   ):
    withdraw = round(amount * ((100+penalty_percent)/100))
    to_pay = round(amount * ((100+bonus_percent)/100))

    if from_team.wallet < withdraw:
        withdraw -= from_team.wallet
        from_team.wallet = 0
        from_team.bank -= withdraw
    
    to_team.wallet += to_pay
    to_team.save()
    from_team.save()

    #TODO withdraw