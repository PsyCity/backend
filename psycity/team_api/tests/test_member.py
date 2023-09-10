from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status

from team_api import  serializers

from core.models import (
    Player,
    Team,
    PlayerRole,
    TeamJoinRequest
)

# Create your tests here.


class BaseTest(TestCase):

    def setUp(self) -> None:
        roles = []
        for role in PlayerRole.ROLES_CHOICES.choices:
            roles.append(PlayerRole.objects.create(name=role[0]))

        self.team1   = Team.objects.create(level=1) 

        player1 = Player.objects.create(team=self.team1)
        self.player1 = player1
        
        player2 = Player.objects.create(team=self.team1)
        player3 = Player.objects.create(team=self.team1)
        
        return super().setUp()
    

class RoleTest(BaseTest):

    def test_add_role(self):
        player = Player.objects.last()
        role = PlayerRole.objects.get(name="Nerd")

        response = self.patch_call(
            role=role.name,
            todo="add",
            agreement=3,
            player=player
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertTrue(
            role in player.player_role.all()
        )

    def test_remove_role(self):
        role = PlayerRole.objects.get(name="Nerd")

        response = self.patch_call(
            role= role.name,
            todo="delete",
            agreement=3
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.content
        )
        player = Player.objects.get(pk=self.player1.pk)
        
        self.assertTrue(
            role not in player.player_role.all()
        )


    def test_serializer(self):
        
        data = {
            "role":"qwerty",
            "todo" : "add"
        }
        
        serializer = serializers.TeamMemberSerializer(data=data)
        
        self.assertEqual(
            serializer.is_valid(),
            False,
        )
        
    def test_role_not_set(self):
        response = self.patch_call(
            role=None,
            todo="add",
            agreement=3
        )
        
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        
    def test_todo_not_set(self):
        
        response = self.patch_call(
            role="Nerd",
            todo=None,
            agreement=3
        )
        
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def patch_call(self, role, todo, agreement, player=None):

        player = player or self.player1

        url = reverse("team_api:role-detail", kwargs={"pk":player.pk})

        c = Client()
        response = c.patch(
            path=url,
            data={
                "agreement" : agreement,
                "todo" : todo,
                "role" : role
            },
            content_type="application/json"
        )
        return response

class KickTest(BaseTest):
    def setUp(self) -> None:
        super().setUp()
        player4 = Player.objects.create(team=self.team1)



    def test_kick_properly(self):
        response = self.patch_caller(
            agreement=3,
            player_id=self.player1.pk
        )
        
        self.assertEqual(
            response.status_code,
            200
        )

        player = Player.objects.get(pk=self.player1.pk)
        
        self.assertEqual(
            player.team,
            None
        )

        self.assertEqual(
            player.status,
            player.STATUS_CHOICES[1][0]
        )

    def test_player_not_exist(self):
        
        response = self.patch_caller(
            agreement=3,
            player_id=123
        )
        
        self.assertEqual(
            response.status_code,
            404
        )

    def test_homeless_player(self):
        homeless = Player.objects.create()

        response = self.patch_caller(
            agreement=0,
            player_id=homeless.pk
        )
        
        self.assertEqual(
            response.status_code,
            400,
            msg=response.content
        )

    def test_agreement(self):
        response = self.patch_caller(
            agreement=2,
            player_id=3
        )

        self.assertEqual(
            response.status_code,
            406,
            response.content
        )

    def test_lack_of_team_member(self):
        team = Team.objects.create(level=2)
        Player.objects.create(team=team)
        player = Player.objects.create(team=team)
        

        response = self.patch_caller(
            agreement=1,
            player_id=player.pk
        )

        self.assertEqual(
            response.status_code,
            406
        )
    def test_validation(self):
        serializer = serializers.TeamMemberSerializer(data={}) 
        
        self.assertEqual(
            serializer.is_valid(),
            False
        )

    def test_method_not_allowed(self):
        c = Client()
        url = reverse("team_api:kick-detail", kwargs={"pk" : 1})

        get_response = c.get(url)
        post_response = c.post(url)
        put_response = c.put(url)

        self.assertTrue(
            get_response.status_code  == \
            put_response.status_code  == \
            post_response.status_code ==\
            405,
        )
        
    def patch_caller(self, agreement, player_id):
        data = {
            "agreement" : agreement
        }
        url = reverse("team_api:kick-detail", kwargs={"pk" : player_id})
        c = Client()
        return c.patch(url, data, "application/json")



class InviteTest(BaseTest):
    def setUp(self) -> None:
        
        super().setUp()
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