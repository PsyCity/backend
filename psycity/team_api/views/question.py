from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.exceptions import ValidationError, NotAcceptable
from rest_framework.parsers import MultiPartParser
from rest_framework import status

from core.models import Question, Team, Player, ConstantConfig, TeamQuestionRel, QuesionSolveTries, Contract
from team_api import serializers, schema
from rest_framework.response import Response
from team_api.utils import ResponseStructure
from core.config import QUESTION_SOLVE_LIMIT_PER_HOUR
from team_api.judge import CodeJudgeService

from django.utils.timezone import datetime, timedelta, make_aware
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile

from team_api.utils import game_state
import os
import uuid
import zipfile
import shutil
from pathlib import Path



class QuestionBuyView(GenericAPIView):
    serializer_class = serializers.QuestionBuySerializer

    @game_state()
    def post(self, request, *args, **kwargs):
        try:
            conf = ConstantConfig.objects.latest('id')
            question = Question.objects.get(pk=request.data['question_id'])
            team = Team.objects.get(pk=request.data['team_id'])
            team_bought_questions_till_last_night = TeamQuestionRel.objects.filter(team=team, created_date__date=datetime.today()).count()
            bought_and_solve_before = TeamQuestionRel.objects.filter(team=team, question=question, solved=True)

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
            if question.last_owner and question.last_owner == team:
                return Response({
                    "message": "soal ghablan kharidari shode",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)

            if not question.is_published:
                return Response({
                    "message": "question is not published!",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)
            if bought_and_solve_before:
                return Response({
                    "message": "You bought and solved this question before",
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

            calculated_price = question.price * conf.inflation_coefficient
            team.wallet -= calculated_price
            question.last_owner = team
            question.price = calculated_price
            team.today_bought_question = team.today_bought_question
            new_team_question_rel = TeamQuestionRel(team=team, question=question)
            question.is_published = False

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

    @game_state(["Day"])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question_type = serializer.validated_data.get("question_type")
        team_id = serializer.validated_data.get("team_id")
        player_id = serializer.validated_data.get("player_id")
        text_answer = serializer.validated_data.get("text_answer")
        file_answer = serializer.validated_data.get("file_answer")

        player = None
        team = None
        contract = None

        conf = ConstantConfig.objects.latest('id')

        if not conf:
            return Response({
                "message": "define constant configs first!",
                "data": [],
                "result": None,
            }, status=status.HTTP_400_BAD_REQUEST)

        if not team_id and not player_id:
            return Response({
                "message": "Provide either team_id or player_id",
                "data": [],
                "result": None,
            }, status=status.HTTP_400_BAD_REQUEST)
        if team_id and player_id:
            return Response({
                "message": "One of team_id or player_id must be filled",
                "data": [],
                "result": None,
            }, status=status.HTTP_400_BAD_REQUEST)

        if not text_answer and not file_answer:
            return Response({
                "message": "Provide either text or file answer",
                "data": [],
                "result": None,
            }, status=status.HTTP_400_BAD_REQUEST)

        question = Question.objects.filter(pk=serializer.validated_data.get("question_id"))
        if not question:
            return Response({
                    "message": "Question not found",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_404_NOT_FOUND)
        question = question.first()

        if question.qtype != question_type:
            return Response({
                "message": "Invalid question type",
                "data": [],
                "result": None,
            }, status=status.HTTP_400_BAD_REQUEST)

        if team_id:
            team = get_object_or_404(Team, pk=team_id)
            if question.last_owner != team:
                return Response({
                    "message": "Question does not belong to the specified team",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)
        elif player_id:
            player = Player.filter(pk=player_id, status='Bikhaanemaan')
            if not player:
                return Response({
                    "message": "Player not found or player is not Bikhaanemaan",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_404_NOT_FOUND)
            player = player.first()
            contract_query = Contract.objects.filter(
                state=2,
                contract_type='homeless_solve_question',
                second_party_player=player,
                first_party_agree=True,
                second_party_agree=True,
                question=question,
                archive=False,
            )
            if not contract_query:
                return Response({
                    "message": "There is no contract between this player and a team",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)
            contract = contract_query.first()

        team_question_rel = TeamQuestionRel.objects.get(question=question, team=team)        

        # solve procedure
        last_hour_datetime = datetime.now() - timedelta(hours=1)
        solve_tries = QuesionSolveTries.objects.filter(Q(team=team, question=question) | Q(player=player_id, question=question))
        last_hour_tries = solve_tries.filter(created_date__gte=last_hour_datetime)
        solved_before = solve_tries.filter(solved=True)
        max_received_score_query = solve_tries.order_by('-received_score').first()
        max_received_score = max_received_score_query.received_score if max_received_score_query else 0

        if last_hour_tries.count() >= QUESTION_SOLVE_LIMIT_PER_HOUR:
            return Response({
                    "message": "Your number of attempts to solve the question has exceeded the limit",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)

        if solved_before:
            return Response({
                    "message": "You cannot solve the question that you solved before",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)
        
        target_question = QuesionSolveTries.objects.create(
                    team=team if team else None,
                    player=player if player else None,
                    question=question,
                    solved=False,
                    received_score=0,
                    homeless_contract=contract if contract else None,
                    answer_text=text_answer if text_answer else None,
                )
        if file_answer:
            target_question.answer_file.save(file_answer.name, ContentFile(file_answer.read()))
            target_question.save()

        # FIXME: handle player solve question

        if question_type == 1:
            qprice = question.price
            if text_answer.strip() == question.answer_text.strip():
                delay = (make_aware(datetime.now()) - team_question_rel.created_date).seconds // 60
                if question.level == 1:
                    delayed = delay <= conf.question_level_1_early_solve_time
                    score = qprice * (conf.delay_factor if delayed else 2)
                elif question.level == 2:
                    delayed = delay <= conf.question_level_2_early_solve_time
                    score = qprice * (conf.delay_factor if delayed else 2)
                else:
                    delayed = delay <= conf.question_level_3_early_solve_time
                    score = qprice * (conf.delay_factor if delayed else 2)

                target_question.solved = True
                target_question.received_score = score
                target_question.solved = True
                team_question_rel.solved = True
                team_question_rel.received_score = score

                if team:
                    team.wallet += score
                    team.save()
                else:
                    player.wallet += score
                    player.save()

                target_question.save()
                team.save()
                team_question_rel.save()
                #FIXME: if homeless solve the question the contract automatically apllied?
            else:
                return Response({
                    "message": "Incorrect answer",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)

        elif question_type == 2:
            answer_zip_file = question.answer_file.file
            extract_dir = f'data_dir/questionsolvetries_judge/{str(uuid.uuid4())}'
            extract_dir_Path = Path(extract_dir)
            extract_dir_Path.mkdir(parents=True)

            with zipfile.ZipFile(answer_zip_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            code_file_path = os.path.join(extract_dir, file_answer.name)
            with open(code_file_path, 'wb') as code_file:
                for chunk in file_answer.chunks():
                    code_file.write(chunk)

            target_question.judge_extract_dir = extract_dir

            try:
                code_judge_service = CodeJudgeService()
                time_limit = question.time_limit or 2
                memory_limit = question.memory_limit or 256
                jresult = code_judge_service.judge(code_file_path, extract_dir, time_limit=time_limit, memory_limit_mb=memory_limit)

                if not jresult[0]:
                    target_question.judge_status = 'fail'
                    target_question.save()
                    return Response({
                        "message": f"khata. {jresult[1]}",
                        "data": [],
                        "result": None,
                    }, status=status.HTTP_400_BAD_REQUEST)
                result = jresult[1]
                rounded_result = round(result * 100)
                target_question.judge_status = 'success'
                target_question.judge_result = result

                delay = (make_aware(datetime.now()) - team_question_rel.created_date).seconds // 60
                qprice = question.price * conf.inflation_coefficient
                if question.level == 1:
                    delayed = delay <= conf.question_level_1_early_solve_time
                    score = qprice * result * (conf.delay_factor if delayed else 2)
                elif question.level == 2:
                    delayed = delay <= conf.question_level_2_early_solve_time
                    score = qprice * result * (conf.delay_factor if delayed else 2)
                else:
                    delayed = delay <= conf.question_level_3_early_solve_time
                    score = qprice * result * (conf.delay_factor if delayed else 2)

                score = int(score)
                if score > max_received_score:
                    if rounded_result == 1:
                        target_question.solved = True
                        target_question.received_score = score
                        team.wallet += (score - max_received_score)
                        target_question.solved = True
                        team_question_rel.solved = True
                        team_question_rel.received_score = score
                    else:
                        target_question.received_score = score
                        team.wallet += (score - max_received_score)
                        team_question_rel.received_score = score
                    
                    target_question.save()
                    team.save()
                    team_question_rel.save()
                    return Response({
                        "message": f"emtiaz: {rounded_result}, meghdar ezafe shode be wallet:{score - max_received_score}",
                        "data": [],
                        "result": None,
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "message": f"az dafe ghab emtiaz bishtari nagerefti :(. emtiaz: {rounded_result}",
                        "data": [],
                        "result": None,
                    }, status=status.HTTP_200_OK)


            except Exception as e:
                target_question.judge_status = e.__str__()
                target_question.save()
                return Response({
                    "message": f"khata dar judge. {e.__str__()}",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({
                    "message": "Invalid question_type",
                    "data": [],
                    "result": None,
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "Question solved successfully",
            "data": [],
            "result": None,
        }, status=status.HTTP_200_OK)


class UpdateQuestionPrice(
    GenericViewSet,
    mixins.ListModelMixin
):
    queryset = Question.objects.all()
    serializer_class = serializers.serializers

    def list(self, request, *args, **kwargs):
        questions = Question.objects.all()
        conf = ConstantConfig.objects.last()

        for question in questions:
            base_price = question.price 
            if question.level == 1 :
                new_price = conf.question_level_0_value
            elif question.level ==2:
                new_price = conf.question_level_1_value
            elif question.level == 3:
                new_price = conf.question_level_2_value
            question.price = new_price
            question.save()
            if question.last_owner:
                team :Team= question.last_owner
                team.wallet -= (new_price - base_price)
                team.save()
                
        return Response()

                
