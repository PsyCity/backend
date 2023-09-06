from django.test import TestCase, Client
from django.urls import reverse
from team_api.utils import ResponseStructure
import json
from core.models import (
    Player,
    Team,
    PlayerRole,
    TeamJoinRequest
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


class KickTest(BaseTest):
    def setUp(self) -> None:
        super().setUp()
        player2 = Player.objects.create(team=self.team1)
        player3 = Player.objects.create(team=self.team1)
        player4 = Player.objects.create(team=self.team1)
    def test_kick_properly(self):
        url = reverse("team_api:kick-detail", kwargs={"pk":1})
        c = Client()
        response = c.patch(url,
                        {"agreement" : []},
                        "application/json")
    
        self.assertEqual(response.status_code, 200)    
    
    def test_invalid_input(self):
        ...
    def test_lack_of_team_player(self):
        ...


class InviteTest(BaseTest):
    def setUp(self) -> None:
        
        super().setUp()

        self.player2 = Player.objects.create(team=self.team1)
        self.player3 = Player.objects.create(team=self.team1)
        self.player4 = Player.objects.create()
        self.url     = reverse("team_api:invite-list")

    def test_agreement(self):
        ...
    def test_other_validations(self):
        ...

    def test_invite_properly(self):
        
        response = self.call_api(
            team_pk=self.team1.pk,
            player_pk=self.player4.pk
        )
        
        self.assertEqual(response.status_code, 201)
        
        invite = \
            TeamJoinRequest.objects.filter(
                player=self.player4
            ).first()
        
        self.assertFalse(invite is None)
        


    def test_team_is_full(self):
        Player.objects.create(team=self.team1)
        response = self.call_api(
            self.team1.pk,
            self.player4.pk
        )
        self.assertEqual(
            response.status_code,
            406,
            response.content)


    def test_player_not_found(self):
        res = self.call_api(
            team_pk=self.team1.pk,
            player_pk=1234
        )

        self.assertEqual(
            res.status_code,
            404,
            res.content)


    def test_team_not_found(self):
        res = self.call_api(
            team_pk=1234,
            player_pk=self.player4.pk,
        )

        self.assertEqual(
            res.status_code,
            404,
            res.content
        )


    def test_not_homeless(self):
        team2 = Team.objects.create(level=3)
        res = self.call_api(
            team_pk=team2.pk,
            player_pk=self.player1.pk
        )

        self.assertFalse(
            res.status_code == 201,
            "sent the player the join-request" 
            )


    def test_methods(self):
        c = Client()
        patch_res   = c.patch(self.url)
        get_res     = c.get(self.url)
        put_res     = c.put(self.url)
        
        self.assertEqual(patch_res.status_code, 405)
        self.assertEqual(put_res.status_code, 405)
        self.assertEqual(get_res.status_code, 405)


    def test_duplicate_invitation(self):
        
        self.call_api(
            team_pk=self.team1.pk,
            player_pk=self.player1.pk
        )
        
        response2 = self.call_api(
            self.team1.pk,
            self.player1.pk
        )
        
        self.assertEqual(
            406,
            response2.status_code,
            response2.content
            )


    def call_api(self, team_pk, player_pk):
        c = Client()
        data = {
            "team" : team_pk,
            "player" : player_pk
        }
        response = c.post(self.url, data)
        return response