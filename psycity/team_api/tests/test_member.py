from django.test import TestCase, Client
from django.urls import reverse_lazy
from team_api.utils import ResponseStructure
import json
from core.models import (
    Player,
    Team,
    Role
) 
# Create your tests here.


BASE_REQUEST = {
    'team_id':1,
    'player_id' : 1,
    'agreement': [], 
}

class RoleTest(TestCase):
    def setUp(self) -> None:
        roles = []
        for role in Role.RoleChoices.choices:
            roles.append(Role.objects.create(name=role[0]))
        self.request = BASE_REQUEST
        player1 = Player.objects.create()
        player1.player_role.set((roles[1],roles[2]))
        self.player1 = player1
        self.team1   = Team.objects.create(level=1) 
        
        return super().setUp()
    
    def test_response_status_code(self):
        c = Client()
        res = c.patch(reverse_lazy("team_api:member-role"))
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
            path=reverse_lazy("team_api:member-role"),
            content_type="application/json",
            data=data)
        self.assertEqual(response.status_code, 200, response.content)

        expected_response = ResponseStructure().data
        returned_data = json.loads(response.content)
        self.assertDictEqual(returned_data, expected_response)

        player = Player.objects.get(pk=data["player_id"])
        role = Role.objects.get(name=role)
        self.assertEqual((role in player.player_role.all()),
                         role_existing_in_player_roles)
