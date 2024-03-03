from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import exceptions, status
from psycity.settings import DEBUG
from core.models import Team, BankDepositBox, Question, Player
from drf_yasg import openapi
from functools import wraps
from abc import ABCMeta


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


class ListModelMixin:
    """
    List a queryset.
    """
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

def team_cost_validation(cost, team:Team):
    if team.wallet < cost:
        raise exceptions.NotAcceptable(
            f"Team {team.name} cant effort {cost} amount of money"
        )
        # log.warning(f"Team {team.name} cant effort {cost} amount of money")
    return True

def player_cost_validation(cost, player: Player):
    if player.wallet < cost:
        raise exceptions.NotAcceptable(
            f"Player {player.name} cant effort {cost} amount of money"
        )
        # log.warning(f"Player {player.name} cant effort {cost} amount of money")
    return True

def question_validation(question: Question, first_team: Team):
     if question.last_owner != first_team:
         raise exceptions.NotAcceptable(
             f"Quesiton owner is not first party team"
         )
     return True
    
    
def response(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        
        except exceptions.ValidationError as e:
            return Response(
                data={
                    "message": "Validation Error.",
                    "data": [e.detail]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except exceptions.NotAcceptable as e:
            return Response(
                data={
                    "message": "Request is not acceptable.",
                    "data":[e.__str__() if DEBUG else None],
                    "result": None
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        
        except Http404:
            return Response(
                data={
                    "message": "Not Found.",
                    "data": [],
                    "result": None
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            return Response(
                data={
                    "message": "Something went wrong.",
                    "data":[e.__str__() if DEBUG else None],
                    "result": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    return wrapper


def find_boxes(box: BankDepositBox) -> set:
    
    if parent:=box.parent_box:
        boxes = list(parent.bankdispositbox_parent_box.all())
        boxes.append(parent)
    elif childs:=box.bankdispositbox_parent_box.all():
        boxes = list(childs)
        boxes.append(box)
    else:
        boxes = [box]

    return set(boxes)


class ModelSerializerAndABCMetaClass(
    type(serializers.ModelSerializer),
    ABCMeta
    ): ...
