from collections.abc import Iterable
from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions 
from django.utils.html import mark_safe
from core.utiles import PathAndRename
from random import randint
import time


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class WarehouseBox(BaseModel):

    BOX_STATUS = (
        (0, "Lock"),
        (1, "Robbed"),
        (2, "Empty by citizen")
    )
    LEVEL_CHOICE = [
        (1, 'Level 1'),
        (2, 'Level 2'),
        (3, 'Level 3')
    ]
    lock_state = models.IntegerField(_("Lock State"),
                                     choices=BOX_STATUS,
                                     default=0)
    box_number = models.IntegerField(_("Box Number"), null=False, blank=False)
    sensor_state = models.BooleanField(default=False)
    level = models.IntegerField(choices=LEVEL_CHOICE)

    unlocker = models.ForeignKey("Team",
                                 on_delete=models.CASCADE,
                                 related_name='warehouse_box_unlocker',
                                 blank=True,
                                 null=True
                                 )
    
    sensor_hacker = models.ForeignKey("Team",
                                      on_delete=models.CASCADE,
                                      related_name='warehouse_box_sensor_hacker',
                                      blank=True,
                                      null=True
                                      )
    expiration_date = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    lock_question = models.ForeignKey("WarehouseQuestions",
                                 on_delete=models.CASCADE,
                                 related_name='warehouse_box_question',
                                 null=True
                                 )
    box_question    = models.ForeignKey("Question",
                                        verbose_name=_("question inside the box"),
                                        on_delete=models.CASCADE
                                        )
       
    money = models.PositiveIntegerField(default=0)
    @property
    def is_lock(self):
        return self.lock_state==0
    
    @property
    def worth(self):
        return self.box_question.price + self.money


class BankDepositBox(BaseModel):
    SENSOR_STATE_CHOICE = [
        (0, 'Not Installed'),
        (1, 'Installed'),
    ]

    money = models.PositiveIntegerField(default=0)
    password = models.IntegerField()
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

    def save(self, *args, **kwargs) -> None:
        if self.password is None:
            self.password = randint(1000, 9999)
        return super().save(*args, **kwargs)


class ConstantConfig(BaseModel):
    GAME_STATUS = [
        (0, "Night"),
        (1, "Day"),
        (2, "Off")
    ]
    game_current_state = models.IntegerField(choices=GAME_STATUS)
    wallet_init_value = models.IntegerField(default=900)
    question_level_0_value = models.IntegerField(default=200)
    question_level_1_value = models.IntegerField(default=400)
    question_level_2_value = models.IntegerField(default=800)
    question_solve_interest_percent = models.PositiveIntegerField(default=200)
    bought_question_max = models.PositiveIntegerField(default=12)
    contract_tax = models.FloatField(default=0.05)
    inflation_coefficient = models.FloatField(default=1)
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
    team_loan_percent_max = models.FloatField(default=1.2)
    team_escape_room_max = models.PositiveIntegerField(default=2)
    bank_robbery_contract_sponsorship_max = models.PositiveIntegerField(default=2)
    police_sensor_contract_sponsorship_max = models.PositiveIntegerField(default=5)
    # escape_room_solve_time = models.PositiveIntegerField()

    def state_converter(self):
        state_int = self.game_current_state
        
        if state_int == 0:
            return "Night"
        elif state_int == 1:
            return "Day"
        else:
            return "Off"
    @property
    def state(self):
        return self.state_converter()
class Player(BaseModel):


    STATUS_CHOICES = [
        ('TeamMember', 'Team Member'),
        ('Bikhaanemaan', 'Bikhaanemaan'),
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
    discord_id = models.BigIntegerField(null=False, blank=False, unique=True, primary_key=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Team(BaseModel):
    ROLES_CHOICES = [
        ('Mafia', 'Mafia'),
        ('Polis', 'Polis'),
        ('Shahrvand', 'Shahrvand'),
    ]

    STATE_CHOICE = [
        ('Active', 'Active'),
        ('Disbanded', 'Disbanded')
    ]

    def generate_hidden_id():
        new_hidden_id = randint(100, 999)
        return new_hidden_id

    name = models.CharField(max_length=35)
    team_role = models.CharField(max_length=20, choices=ROLES_CHOICES)
    state = models.CharField(max_length=20, choices=STATE_CHOICE)
    wallet = models.IntegerField(default=0)
    bank = models.IntegerField(default=0)
    level = models.PositiveIntegerField(validators=[
            MinValueValidator(1, message='Value must be greater than or equal to 1.'),
            MaxValueValidator(10, message='Value must be less than or equal to 10.'),
        ])
    bank_liabilities = models.IntegerField(default=0)
    max_bank_loan = models.IntegerField(default=0)
    last_bank_action = models.DateTimeField(blank=True, null=True)
    today_bought_question = models.IntegerField(default=0)
    channel_id = models.IntegerField()
    channel_role = models.BigIntegerField(null=False, blank=False, unique=True, primary_key=True)
    hidden_id = models.IntegerField(unique=True, validators=[
                                    MinValueValidator(100, message='Value must be greater than or equal to 100.'),
                                    MaxValueValidator(999, message='Value must be less than or equal to 999.')])
    has_card = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def total_asset(self):
        return self.wallet + (self.bank - self.bank_liabilities)


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
    price = models.IntegerField(default=1)
    score = models.IntegerField(default=1)
    is_published = models.BooleanField(default=False)
    title = models.CharField(max_length=300)
    body = models.ImageField(upload_to=PathAndRename('data_dir/question'))
    qtype = models.IntegerField(choices=TYPE_CHOICE)
    answer_text = models.TextField(blank=True, null=True)
    answer_file = models.FileField(blank=True, null=True, upload_to='data_dir/question_answer_file')
    attachment = models.FileField(blank=True, null=True, upload_to='data_dir/question_attachment')
    attachment_link = models.CharField(max_length=100, null=True, blank=True)
    memory_limit = models.IntegerField(default=256, null=True, blank=True)
    time_limit = models.IntegerField(default=2, null=True, blank=True)

    def body_preview(self): #new
        return mark_safe(f'<img src = "{self.body.url}" width = "300"/>')

    


class TeamQuestionRel(BaseModel):
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='teamquestionrel_team')
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name='teamquestionrel_question')
    solved = models.BooleanField(default=False)
    received_score = models.IntegerField(default=False)
    tries = models.IntegerField(default=False)

    def __str__(self) -> str:
        return f'{self.pk} - {self.question}'

class PlayerQuestionRel(BaseModel):
    player = models.ForeignKey("Player", on_delete=models.CASCADE, related_name="playerquestionrel_player")
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name="playerquestionrel_question")    
    solved = models.BooleanField(default=False)
    received_score = models.IntegerField(default=False)
    tries = models.IntegerField(default=False)

class QuesionSolveTries(BaseModel):
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='question_solve_tries_team', blank=True, null=True)
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='question_solve_tries_player', blank=True, null=True)
    homeless_contract = models.ForeignKey('Contract', on_delete=models.CASCADE, related_name='question_solve_tries_contract', blank=True, null=True)
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name='question_solve_tries_question')
    solved = models.BooleanField(default=False)
    received_score = models.IntegerField(default=False)
    answer_text = models.TextField(null=True, blank=True)
    answer_file = models.FileField(blank=True, null=True, upload_to='data_dir/questionsolvetries_answer_file')
    judge_result = models.FloatField(null=True, blank=True)
    judge_status = models.CharField(max_length=200, null=True, blank=True)
    judge_extract_dir = models.CharField(max_length=200, null=True, blank=True)

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
        homeless_solve_question = 'homeless_solve_question', _('Homeless Solve Question'),
        other = 'other', _('Other'),
    
    state = models.IntegerField(choices=STATE_CHOICE)
    contract_type = models.CharField(max_length=40, choices=CONTRACT_TYPES.choices)
    cost    = models.IntegerField(default=0)
    first_party_player = models.ForeignKey("Player",
                                           on_delete=models.CASCADE,
                                           null=True,
                                           blank=True,
                                           related_name='contract_first_party_to_player'
                                           )

    first_party_team = models.ForeignKey("Team",
                                         on_delete=models.CASCADE,
                                         null=True,
                                         blank=True,
                                         related_name='contract_first_party_to_team'
                                         )
    
    second_party_player = models.ForeignKey("Player",
                                            on_delete=models.CASCADE,
                                            related_name='contract_second_party_to_player',
                                            null=True,
                                            blank=True,
                                            )

    second_party_team = models.ForeignKey("Team",
                                          on_delete=models.CASCADE,
                                          related_name='contract_second_party_to_team',
                                          null=True,
                                          blank=True,
                                          )

    terms = models.TextField()
    question = models.ForeignKey('Question',
                                    on_delete=models.CASCADE,
                                    related_name='contract_question_to_question',
                                    blank=True,
                                    null=True)
    first_party_agree = models.BooleanField()
    second_party_agree = models.BooleanField()
    first_party_confirm = models.BooleanField(default=False)
    second_party_confirm = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    archive = models.BooleanField() # todo isn't it avail in state?
    is_rejected = models.BooleanField(default=False)


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
    discord_role_id = models.BigIntegerField(null=False, blank=False, unique=True, primary_key=True)

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




class WarehouseQuestions(BaseModel):
    text    = models.TextField(_("Question text"))
    answer  = models.TextField(_("Question answer")) 
    attachment = models.FileField(blank=True, null=True, upload_to='data_dir/warehousequestion_attachment')
    attachment_link = models.CharField(max_length=100, null=True, blank=True)

class BankSensorInstall(BaseModel):

    STATE_CHOICE=[
        (1, "Created"),
        (2, "Used"),
        (3, "Solved"),
        (4, "Failed")
    ]
    
    state       = models.IntegerField(choices=STATE_CHOICE ,default=1)
    contract    = models.ForeignKey("Contract", on_delete=models.DO_NOTHING)
    police      = models.ForeignKey("Team",
                                    on_delete=models.DO_NOTHING,
                                    related_name="bank_sensor_police"
                                    )
    citizen     = models.ForeignKey("Team",
                                    on_delete=models.DO_NOTHING,
                                    related_name="bank_sensor_citizen",
                                    )
    room        = models.ForeignKey("EscapeRoom",
                                    verbose_name=_("selected room for citizen"),
                                    on_delete=models.CASCADE,
                                    null=True
                                    )
    opening_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _("bank sensor install request")
        verbose_name_plural = _("bank sensor install requests")


class Report(
    BaseModel
    ):

    REPORT_TYPE = (
        (1, "Simple Report"),
        (2, "Contract Report")
    )

    description = models.TextField(
        _("Report Description"),
        null=True,
        blank=True
        )
    
    report_type = models.IntegerField(
        _("Report Type"),
        choices=REPORT_TYPE,
        default=1
        )

    player_reporter = models.ForeignKey(
        "Player",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True
        )
    
    team_reporter = models.ForeignKey(
        "Team",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True
        )
    
    contract = models.ForeignKey(
        "Contract",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True
        )
    

class TransferMoney(
    BaseModel
):
    from_team = models.ForeignKey("Team",null=True, blank=True, on_delete=models.CASCADE, related_name="transfer_money_team_1")
    to_team = models.ForeignKey("Team",null=True, blank=True, on_delete=models.CASCADE, related_name="transfer_money_team_2")
    from_player = models.ForeignKey("Player", null=True, blank=True, on_delete=models.CASCADE, related_name="transfer_money_player_1")
    to_player = models.ForeignKey("Player", null=True, blank=True, on_delete=models.CASCADE, related_name="transfer_money_player_2")
    amount = models.IntegerField()
    
    def save(self, *args, **kwargs):
        if self.from_team and self.from_team.wallet > self.amount:
            self.from_team.wallet -= self.amount
            self.from_team.save()
        elif self.from_player and self.from_player.wallet > self.amount:
            self.from_player.wallet -= self.amount
            self.from_player.save()

        else:
            raise exceptions.NotAcceptable("shekast dar enteghal: mojodi kam")
        
        if self.to_team:
            self.to_team.wallet += self.amount
            self.to_team.save()
        elif self.to_player:
            self.to_player.wallet += self.amount
            self.to_player.save()

        else:
            raise exceptions.NotAcceptable(" ye chisi eshtebah shod")
        return super().save(*args, **kwargs)
    

class MoneyChangeLogger(BaseModel):

    from_team = models.ForeignKey("Team", null=True, blank=True, on_delete=models.CASCADE, related_name="money_change_logger_from_team")
    to_team = models.ForeignKey("Team", null=True, blank=True, on_delete=models.CASCADE, related_name="money_change_logger_to_team")
    amount = models.IntegerField(null=True, blank=True)
    warehouse_box = models.ForeignKey("WarehouseBox", null=True, blank=True, on_delete=models.CASCADE, related_name="money_change_logger_warehous_box")
    before_wallet = models.IntegerField(null=True, blank=True)
    current_wallet = models.IntegerField(null=True, blank=True)
