from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe
from core.utiles import PathAndRename
from random import randint


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class WarehouseBox(BaseModel):
    is_lock = models.BooleanField(default=True)
    unlocker = models.ForeignKey("Player", on_delete=models.CASCADE, related_name='warehouse_box_unlocker')
    sensor_state = models.BooleanField(default=False)
    sensor_hacker = models.ForeignKey("Player", on_delete=models.CASCADE, related_name='warehouse_box_sensor_hacker')
    expiration_date = models.DateTimeField(auto_now_add=False)
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name='warehouse_box_question')
    money = models.PositiveIntegerField()

class BankDepositBox(BaseModel):
    SENSOR_STATE_CHOICE = [
        (0, 'Not Installed'),
        (1, 'Installed'),
    ]

    money = models.PositiveIntegerField(default=0)
    password = models.IntegerField(default=randint(1000,9999))
    robbery_state = models.BooleanField(default=False)
    reported = models.BooleanField(default=False)
    rubbery_team = models.ForeignKey("Team",
                                     on_delete=models.DO_NOTHING,
                                     related_name="bankdispositbox_rubbery_team",
                                     blank=True,
                                     null=True
                                     )
    
    sensor_state = models.IntegerField(choices=SENSOR_STATE_CHOICE, default=0)

    sensor_owner = models.ForeignKey("Team",
                                     on_delete=models.DO_NOTHING,
                                     related_name="bankdispositbox_sensor_owner",
                                     blank=True,
                                     null=True
                                    )
                                    
    is_copy = models.BooleanField(default=False)
    parent_box = models.ForeignKey('self', on_delete=models.CASCADE, related_name="bankdispositbox_parent_box", null=True, blank=True)



class ConstantConfig(BaseModel):
    GAME_STATUS = [
        (0, "Night"),
        (1, "Day")
    ]
    game_current_state = models.IntegerField(choices=GAME_STATUS)
    wallet_init_value = models.IntegerField(default=900)
    question_level_0_value = models.IntegerField(default=200)
    question_level_1_value = models.IntegerField(default=400)
    question_level_2_value = models.IntegerField(default=800)
    question_solve_interest_percent = models.PositiveIntegerField(default=200)
    bought_question_max = models.PositiveIntegerField(default=12)
    contract_tax = models.PositiveIntegerField(default=50)
    # inflation_coefficient = models.FloatField()
    delay_factor = models.FloatField(default=0.7)
    question_level_0_max_try = models.PositiveIntegerField(default=1)
    question_level_1_max_try = models.PositiveIntegerField(default=2)
    question_level_2_max_try = models.PositiveIntegerField(default=3)
    question_code_max_try = models.IntegerField(default=1000)
    question_level_0_early_solve_time = models.PositiveIntegerField(default=40)
    question_level_1_early_solve_time = models.PositiveIntegerField(default=80)
    question_level_2_early_solve_time = models.PositiveIntegerField(default=150)
    deposit_interest_percent = models.PositiveIntegerField(default=3)
    deposit_interest_day_time = models.PositiveIntegerField(default=20)
    deposit_interest_night_time = models.PositiveIntegerField(default=90)
    loan_interest_percent = models.PositiveIntegerField(default=3)
    loan_interest_day_time = models.PositiveIntegerField(default=20)
    loan_interest_night_time = models.PositiveIntegerField(default=90)
    bonus_percent = models.PositiveIntegerField(default=10)
    penalty_percent = models.PositiveIntegerField(default=10)
    subsidy_percentage = models.PositiveIntegerField(default=33) #TODO: changed
    mafia_prison_per_report_time = models.PositiveIntegerField(default=5)
    assassination_attempt_cooldown_time = models.PositiveIntegerField(default=90)
    team_bank_transaction_cooldown = models.PositiveIntegerField(default=30)
    # team_total_bank_value = models.PositiveIntegerField()
    team_loan_percent_max = models.PositiveIntegerField(default=20)
    team_escape_room_max = models.PositiveIntegerField(default=2)
    bank_robbery_contract_sponsorship_max = models.PositiveIntegerField(default=2)
    police_sensor_contract_sponsorship_max = models.PositiveIntegerField(default=5)
    # escape_room_solve_time = models.PositiveIntegerField()


class Player(BaseModel):


    STATUS_CHOICES = [
        ('TeamMember', 'Team Member'),
        ('Homeless', 'Homeless'),
        ('Dead', 'Dead'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    university = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField()
    postal_code = models.CharField(max_length=10)
    mobile = models.CharField(max_length=20)
    discord_username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    player_role = models.ManyToManyField('PlayerRole', blank=True)
    team = models.ForeignKey('Team',
                                on_delete=models.CASCADE,
                                related_name='player_team',
                                blank=True,
                                null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    wallet = models.IntegerField(default=0)
    bank_liabilities = models.IntegerField(default=0)
    last_assassination_attempt = models.DateTimeField(blank=True, null=True) # todo
    bodyguard_team = models.ForeignKey('Team',
                                          blank=True,
                                          null=True,
                                          on_delete=models.DO_NOTHING,
                                          related_name='player_bodyguard_team')
    last_bodyguard_cost = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Team(BaseModel):
    ROLES_CHOICES = [
        ('Mafia', 'Mafia'),
        ('Police', 'Police'),
        ('Citizen', 'Citizen'),
    ]

    STATE_CHOICE = [
        ('Active', 'Active'),
        ('Disbanded', 'Disbanded')
    ]

    name = models.CharField(max_length=35)
    team_role = models.CharField(max_length=20, choices=ROLES_CHOICES)
    state = models.CharField(max_length=20, choices=STATE_CHOICE)
    wallet = models.IntegerField(default=0)
    bank = models.IntegerField(default=0)
    total_asset = models.IntegerField(default=0)
    level = models.PositiveIntegerField(validators=[
            MinValueValidator(1, message='Value must be greater than or equal to 1.'),
            MaxValueValidator(10, message='Value must be less than or equal to 10.'),
        ])
    bank_liabilities = models.IntegerField(default=0)
    max_bank_loan = models.IntegerField(default=0)
    last_bank_action = models.DateTimeField(blank=True, null=True)
    today_bought_question = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class TeamFeature(BaseModel):
    team = models.ForeignKey(
        "Team",
        on_delete=models.CASCADE,
        related_name="team_feature",
        null=True,
        blank=True,
        )
    mafia_last_night_report = models.IntegerField(default=0)
    mafia_opened_night_escape_rooms = models.IntegerField(default=0)
    mafia_reserved_escape_room = models.IntegerField(default=0)
    police_opened_night_escape_rooms = models.IntegerField(default=0)
    police_sensor_request_contracts = models.IntegerField(default=0)
    police_in_analysis_boxes = models.IntegerField(default=0)
    citizen_opened_night_escape_rooms = models.IntegerField(default=0)
    citizen_theft_request_contracts = models.IntegerField(default=0)

class Question(BaseModel):
    LEVEL_CHOICE = [
        (1, 'Level 1'),
        (2, 'Level 2'),
        (3, 'Level 3')
    ]
    TYPE_CHOICE = [
        (1, 'Short answer'),
        (2, 'Code'),
    ]
    level = models.IntegerField(choices=LEVEL_CHOICE)
    last_owner = models.ForeignKey('Team',
                                   on_delete=models.CASCADE,
                                   related_name='question_last_owner_id',
                                   blank=True,
                                   null=True
                                   )
    price = models.IntegerField()
    score = models.IntegerField()
    is_published = models.BooleanField(default=False)
    title = models.CharField(max_length=300)
    body = models.ImageField(upload_to=PathAndRename('data_dir/question'))
    qtype = models.IntegerField(choices=TYPE_CHOICE)
    answer_text = models.TextField(blank=True, null=True)
    answer_file = models.FileField(blank=True, null=True, upload_to='question_answer_file')
    no_valid_tries = models.IntegerField()
    valid_solve_minutes = models.IntegerField()

    def body_preview(self): #new
        return mark_safe(f'<img src = "{self.body.url}" width = "300"/>')

    


class TeamQuestionRel(BaseModel):
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='teamquestionrel_team')
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name='teamquestionrel_question')
    solved = models.BooleanField()
    received_score = models.IntegerField()
    tries = models.IntegerField()


class EscapeRoom(BaseModel):
    ESCAPE_ROOM_STATE = [
        (0, "base_state"),
        (1, "robbed"),
        (2, "solving"),
        (3, "solved"),
        (4, "failed_to_solve"),
        (5, "reserved for robbery")
    ]

    no_valid_citizen = models.IntegerField()
    no_valid_police = models.IntegerField()
    no_valid_mafia = models.IntegerField()
    solve_time = models.PositiveIntegerField(_("time to solve :min"))
    bank_deposit_box = models.ForeignKey("BankDepositBox",
                                         on_delete=models.DO_NOTHING,
                                         related_name='escape_room',
                                         null=True,
                                         blank=True)

    state = models.IntegerField(choices=ESCAPE_ROOM_STATE, default=0)
    solver_police = models.ForeignKey("Team",
                                      models.DO_NOTHING,
                                      null=True,
                                      blank=True
                                      )


class Contract(BaseModel):
    STATE_CHOICE = [
        (0, 'look for second part'),
        (1, 'waiting for sign'),
        (2, 'waiting to be done'),
        (3, 'archived')
    ]
    class CONTRACT_TYPES(models.TextChoices):
        question_ownership_transfer = 'question_ownership_transfer', _('Question Ownership Transfer'),
        bank_rubbery_sponsorship = 'bank_rubbery_sponsorship', _('Bank Robbery Sponsorship'),
        bank_sensor_installation_sponsorship = 'bank_sensor_installation_sponsorship', _('Bank Sensor Installation Sponsorship'),
        bodyguard_for_the_homeless = 'bodyguard_for_the_homeless', _('Bodyguard for the Homeless'),
        other = 'other', _('Other'),
    
    state = models.IntegerField(choices=STATE_CHOICE)
    contract_type = models.CharField(max_length=40, choices=CONTRACT_TYPES.choices)
    cost    = models.IntegerField(default=0)
    first_party_player = models.ForeignKey("Player",
                                           on_delete=models.CASCADE,
                                           null=True,
                                           related_name='contract_first_party_to_player'
                                           )

    first_party_team = models.ForeignKey("Team",
                                         on_delete=models.CASCADE,
                                         null=True,
                                         related_name='contract_first_party_to_team'
                                         )
    
    second_party_player = models.ForeignKey("Player",
                                            on_delete=models.CASCADE,
                                            related_name='contract_second_party_to_player',
                                            null=True
                                            )

    second_party_team = models.ForeignKey("Team",
                                          on_delete=models.CASCADE,
                                          related_name='contract_second_party_to_team',
                                          null=True
                                          )

    terms = models.TextField()
    first_party_agree = models.BooleanField()
    second_party_agree = models.BooleanField()
    archive = models.BooleanField() # todo isn't it avail in state?


class TeamJoinRequest(BaseModel):
    STATE_CHOICE = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='team_join_request_player')
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='team_join_request_team')
    state = models.CharField(choices=STATE_CHOICE, max_length=30)

class PlayerRole(models.Model):
    class ROLES_CHOICES(models.TextChoices):
        CODE_MASTER = "Code_Master", _("Code Master")
        MASTER_MIND = "MasterMind", _("Master Mind")
        SMOOTH_TALKER = 'SmoothTalker', _('Smooth Talker')

    name = models.CharField(max_length=15, choices=ROLES_CHOICES.choices)

    def __str__(self) -> str:
        return f"{self.name}"
    

class BankRobbery(BaseModel):
    STATE_CHOICE=[
        (1, "Created"),
        (2, "Used"),
        (3, "Solved"),
        (4, "Failed")
    ]
    
    state = models.IntegerField(choices=STATE_CHOICE ,default=1)

    
    mafia = models.ForeignKey(
        "Team",
        verbose_name=_("Mafia Team"),
        on_delete=models.CASCADE,
        related_name="bank_robbery_as_mafia"        
        )
    
    citizen = models.ForeignKey(
        "Team",
        verbose_name=_("Citizen Team"),
        on_delete=models.CASCADE,
        related_name="bank_robbery_as_citizen"
        )
    
    contract = models.ForeignKey(
        "Contract",
        verbose_name=_("bank robbery contract"),
        on_delete=models.CASCADE
        )
    
    escape_room = models.ForeignKey(
        "EscapeRoom",
        on_delete=models.CASCADE,
        related_name="robbery",
        blank=True,
        null=True
        )
    opening_time = models.DateTimeField(blank=True, null=True)
    robbery_amount = models.IntegerField(_("Amount of box money"), blank=True, null=True)