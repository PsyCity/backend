from django.test import TestCase, Client
from django.urls import reverse
from team_api.utils import ResponseStructure
import json
from core.models import (
    Player,
    Team,
    PlayerRole
) 
# Create your tests here.


BASE_REQUEST = {
    'team_id':1,
    'player_id' : 1,
    'agreement': [], 
}


class BaseTest(TestCase):

    def setUp(self) -> None:
        roles = []
        for role in PlayerRole.ROLES_CHOICES.choices:
            roles.append(PlayerRole.objects.create(name=role[0]))
        self.request = BASE_REQUEST
        
        self.team1   = Team.objects.create(level=1) 

        player1 = Player.objects.create(team=self.team1)
        player1.player_role.set((roles[1],roles[2]))
        self.player1 = player1
        
        return super().setUp()
    

class RoleTest(BaseTest):
    def test_response_status_code(self):
        c = Client()
        res = c.patch(reverse("team_api:role-detail", kwargs={"pk":1}))
        self.assertEqual(res.status_code, 400, res.content)

    def test_add_role(self):
        self.set_role("Nerd", "add")

    def test_remove_role(self):
        self.set_role("Nerd", "delete")

    def set_role(self, role, todo):
        if todo=="delete":
            role_existing_in_player_roles = False
        elif todo == "add":
            role_existing_in_player_roles = True
        else:
            raise ValueError("Not an option")

            
        c = Client()
        data = self.request
        data["role"] = role
        data["todo"] = todo 
        response = c.patch(
            path=reverse("team_api:role-detail", kwargs={"pk":1}),
            content_type="application/json",
            data=data)
        self.assertEqual(response.status_code, 200, response.content)

        expected_response = ResponseStructure().data
        returned_data = json.loads(response.content)
        self.assertDictEqual(returned_data, expected_response)

        player = Player.objects.get(pk=data["player_id"])
        role = PlayerRole.objects.get(name=role)
        self.assertEqual((role in player.player_role.all()),
                         role_existing_in_player_roles)
