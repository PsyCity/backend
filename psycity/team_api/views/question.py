from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.exceptions import ValidationError, NotAcceptable
from rest_framework import status

from core.models import Question, Team, Player, ConstantConfig, TeamQuestionRel
from team_api import serializers, schema
from rest_framework.response import Response
from team_api.utils import ResponseStructure

from django.utils.timezone import datetime
from django.db.models import Q


class QuestionBuyView(GenericAPIView):
    serializer_class = serializers.QuestionBuySerializer

    def post(self, request, *args, **kwargs):
        try:
            conf = ConstantConfig.objects.latest('id')
            question = Question.objects.get(pk=request.data['question_id'])
            team = Team.objects.get(pk=request.data['team_id'])
            team_bought_questions_till_last_night = TeamQuestionRel.objects.filter(team=team, created_date__date=datetime.today()).count()

            if not conf:
                return Response({
                    "message": "define constant configs first!",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)
            if team.state == 'inactive':
                return Response({
                    "message": "team is inactive!",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)
            if question.last_owner and question.last_owner != team:
                return Response({
                    "message": "question belong to another team",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)

            if not question.is_published:
                return Response({
                    "message": "question is not published!",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)

            if team_bought_questions_till_last_night >= conf.bought_question_max:
                return Response({
                    "message": "team maximum bought question exceeded!",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)
            if team.wallet < question.price:
                return Response({
                    "message": "team wallet is not enough!",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)

            team.wallet -= question.price
            question.last_owner = team
            new_team_question_rel = TeamQuestionRel(team=team, question=question)

            new_team_question_rel.save()
            team.save()
            question.save()

            return Response({
                "message": f"question {question.title} bought successfully by team {team.name}!",
                "data": [],
                "result": None,
            }, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({
                "message": "question not found",
                "data": [],
                "result": None,
            }, status=status.HTTP_404_NOT_FOUND)
        except Team.DoesNotExist:
            return Response({
                "message": "team not found",
                "data": [],
                "result": None,
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "message": "something went wrong",
                "data": [],
                "result": str(e),
            }, status=status.HTTP_400_BAD_REQUEST)
        
class TeamQuestions(GenericAPIView):
    def get(self, request, team_id, *args, **kwargs):
        team_query = Team.objects.filter(hidden_id=team_id) | Team.objects.filter(channel_role=team_id)
        if not team_query:
            return Response({
                "message": "team not found",
                "data": [],
                "result": None,
            }, status=status.HTTP_404_NOT_FOUND)
        team_id = team_query.first().channel_role
        questions = Question.objects.filter(last_owner=team_id) & Question.objects.filter(is_published=True)
        serializer = serializers.TeamQuestionListSerializer(questions, many=True)
        return Response(serializer.data)