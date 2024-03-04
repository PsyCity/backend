from django.test import TestCase, Client
from django.urls import reverse
# from datetime import datetime
from core.models import (
    Team,
    WarehouseBox,
    ConstantConfig,
    Question,
    WarehouseQuestions
    )
from django.utils import timezone

    
class DepositBoxTest(TestCase):

    def setUp(self) -> None:
        self.conf   = ConstantConfig.objects.create(
            game_current_state=0,
            
        )

        lock = WarehouseQuestions.objects.create(
            answer="qwerty"
        )
        
        q = Question.objects.create(
            level=1,
            price=100,
            score=100,
            qtype=2,
        )
        
        self.box    = WarehouseBox.objects.create(
            expiration_date=timezone.now(),
            box_question=q,
            lock_question=lock,
            money=100
        )
        
        self.mafia  = Team.objects.create(
            level=2
        )
        
        self.cup    = Team.objects.create(
            level=2
        )

        return super().setUp()
    

    def test_robbery_properly(self):
        c = Client()
        response = c.put(
            path= reverse(
                "team_api:warehouse_robbery-detail",
                kwargs={"pk":self.box.pk}
                ),
            data={
                "answer": "qwerty",
                "team": self.mafia.pk
            },
            content_type='application/json'
        )
        self.assertEqual(
            response.status_code,
            200,
            response.content
        )
        self.mafia = Team.objects.get(
            pk=self.mafia.pk
        )
        self.assertEqual(
            self.mafia.wallet,
            self.box.money
        )
        self.box = WarehouseBox.objects.get(
            pk=self.box.pk
            )
        self.assertEqual(
            self.box.is_lock,
            False,
            "OOPS!"
        )
        self.assertEqual(
            self.box.unlocker.pk,
            self.mafia.pk
        )
        

    def test_hack_property(self):
        self.box.lock_state = 1
        self.box.unlocker = self.mafia
        self.box.save()
        c = Client()
        response = c.put(
            path=reverse(
                "team_api:warehouse_hack-detail",
                kwargs={"pk":self.box.pk}
            ),
            data={
                "answer": "qwerty",
                "team"  : self.cup.pk
            },
            content_type="application/json"
        )

        self.assertEqual(
            response.status_code,
            200,
            response.content
        )
        self.cup = Team.objects.get(
            pk=self.cup.pk
        )
        self.assertEqual(
            self.cup.wallet,
            (
             self.conf.bonus_percent *\
              self.box.worth\
                // 100
                )
        )
