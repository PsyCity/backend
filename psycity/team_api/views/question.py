from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.exceptions import ValidationError, NotAcceptable
from rest_framework.parsers import MultiPartParser
from rest_framework import status

from core.models import Question, Team, Player, ConstantConfig, TeamQuestionRel
from team_api import serializers, schema
from rest_framework.response import Response
from team_api.utils import ResponseStructure

from django.utils.timezone import datetime
from django.db.models import Q
from django.shortcuts import get_object_or_404


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
    

class QuestionSolveView(GenericAPIView):
    parser_classes = [MultiPartParser]
    serializer_class = serializers.QuestionSolveSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question_type = serializer.validated_data.get("question_type")
        team_id = serializer.validated_data.get("team_id")
        player_id = serializer.validated_data.get("player_id")
        text_answer = serializer.validated_data.get("text_answer")
        file_answer = serializer.validated_data.get("file_answer")

        # Validate that at least one of team_id and player_id is provided
        if not team_id and not player_id:
            return Response({
                "message": "Provide either team_id or player_id",
                "data": [],
                "result": None,
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate that either text or file answer is provided
        if not text_answer and not file_answer:
            return Response({
                "message": "Provide either text or file answer",
                "data": [],
                "result": None,
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get the question based on the provided question_id
        question = get_object_or_404(Question, pk=serializer.validated_data.get("question_id"))

        # Validate that the question type matches
        if question.qtype != question_type:
            return Response({
                "message": "Invalid question type",
                "data": [],
                "result": None,
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate that the question belongs to the specified team or player
        if team_id:
            team = get_object_or_404(Team, pk=team_id)
            if question.last_owner != team:
                return Response({
                    "message": "Question does not belong to the specified team",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)
        elif player_id:
            player = get_object_or_404(Player, pk=player_id)
            if question.last_owner != player.team:
                return Response({
                    "message": "Question does not belong to the specified player's team",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)

        # Perform additional validation and answer checking based on your requirements

        return Response({
            "message": "Question solved successfully",
            "data": [],
            "result": None,
        }, status=status.HTTP_200_OK)
