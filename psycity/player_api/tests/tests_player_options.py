from django.test import TestCase, Client
from django.urls import reverse

import json

from core.models import Player, Team, TeamJoinRequest
from player_api.views import RESPONSE_BASE
from player_api.serializers import TeamJoinRequestSerializer

class TestJoinRequestTeamAPI(TestCase):
    def setUp(self) -> None:
        self.player = Player.objects.create()
        self.team = Team.objects.create(level=1)
        self.join_request = TeamJoinRequest.objects.create(player_id=self.player,
                                                           team_id=self.team,
                                                           state="active")

    def test_get_join_requests_properly(self):
        expected_data = RESPONSE_BASE
        expected_data["data"] = TeamJoinRequestSerializer(self.join_request).data

        self.get("player_id=1", expected_data, 200)


    def test_get_join_request_no_params(self): #we did'not set the player_id in query
        expected_data = RESPONSE_BASE
        expected_data["status_code"] = 400
        expected_data["message"] = "set the player_id in query_set"
        self.get("", expected_data, 200)  #TODO

        
    def test_patch_join_properly(self):
        data = {}
        expected_data = RESPONSE_BASE
        expected_data["message"] = "player joined the team"
        self.patch(data, 200,expected_data)
        player = Player.objects.first()
        self.assertEqual(player.team_id.id, 1)

    def patch(self, data, code, expected_data):
        c= Client()

        response = c.patch(reverse("player_api:join-detail", kwargs={"pk":1}),
                           data=data,
                           content_type="application/json")

        self.assertEqual(response.status_code,code)
        returned_data = json.loads(response.content)
        self.assertDictEqual(returned_data, expected_data)



    def get(self, query, expected_data, code):
        c = Client()
        response = c.get(reverse("player_api:join-list"),
                         QUERY_STRING=query)
        self.assertEqual(response.status_code,code)
        returned_data = json.loads(response.content)

        self.assertDictEqual(returned_data, expected_data)
