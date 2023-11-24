from django.test import Client, TestCase
from django.urls import reverse

from rest_framework import status

from core.models import (
    Team,
    Contract,
    ConstantConfig,
    EscapeRoom,
    BankRobbery,
    BankDepositBox
)

import json

class Base(
    TestCase,
    ):

    def create_contract(self):
        c = Client()
        response = c.post(
            path=reverse("team_api:contract-list"),
            data={
                "first_party_team": 1,
                "second_party_team": 2,
                "contract_type": "bank_rubbery_sponsorship",
                "cost": 50,
                "terms": "test"
            }
        )
        
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.content
            )
    
    def approve_contract(self):
        c = Client()
        response = c.patch(
            path="/api/v1/team/contract/approvement/1/",

            data={"team":self.mafia.pk},
            content_type="application/json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.content
        )

    def request_bank_robbery(self):
        c = Client()
        response = c.post(
            path="/api/v1/team/action/bank_robbery_way/",
            data={
                "mafia": self.mafia.pk,
                "contract": Contract.objects.last().pk
                }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.content
        )

    def list(self):
        
        c = Client()
        response = c.get(
            path=f"/api/v1/team/action/bank_robbery/?team_id={self.mafia.pk}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.content
        )

        response_content = json.loads(response.content.decode())
        return response_content["data"][0]["robbery_id"]

    def open_escape_room(self, rob_id):

        c = Client()
        response = c.patch(
            path=f"/api/v1/team/action/bank_robbery/{rob_id}/open_escape_room/",
            data={},
            content_type="application/json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.content
        )

    def open_deposit_box(self, rob_id):
        c = Client()
        response = c.post(
            path=f"/api/v1/team/action/bank_robbery/{rob_id}/deposit_box/",
            data={
                "deposit_box": self.box.pk
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.content
        )

class TestBankRobbery(Base):
    def setUp(self) -> None:
        # create some model
        ConstantConfig.objects.create(
            game_current_state=0,
            
        )
        
        self.citizen = Team.objects.create(
            name='citizen_test_team',
            team_role="Citizen",
            wallet=60,
            level=3,
        )
        self.mafia = Team.objects.create(
            name='mafia_test_team',
            team_role="Mafia",
            level=3,
        )
        
        self.escape_room = EscapeRoom.objects.create(
            no_valid_citizen=10,
            no_valid_police=10,
            no_valid_mafia=10,
            solve_time=10,
            state=0,
        )
        self.box = BankDepositBox.objects.create(
            money=100,
            password=1234,
            sensor_state=1,
        )
        return super().setUp()
    
    def test_step_by_step_properly(self):
        self.create_contract()
        self.approve_contract()
        self.request_bank_robbery()
        rob_id = self.list()
        self.open_escape_room(rob_id)
        self.open_deposit_box(rob_id)

    def test_list(self):
        ...

    def test_open_escape_room(self):
        ...

    def test_open_deposit_box(self):
        ...
    
