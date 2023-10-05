from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


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
        (1, 'Installed'),
        (2, 'Not Installed'),
    ]
    money = models.PositiveIntegerField()
    robbery_state = models.BooleanField(default=False)
    rubbery_team = models.ForeignKey("Team", on_delete=models.CASCADE, related_name="bankdispositbox_rubbery_team")
    sensor_state = models.CharField(max_length=30, choices=SENSOR_STATE_CHOICE)
    sensor_owner = models.ForeignKey("Team", on_delete=models.CASCADE, related_name="bankdispositbox_sensor_owner")
    is_copy = models.BooleanField(default=False)
    parent_box = models.ForeignKey('self', on_delete=models.CASCADE, related_name="bankdispositbox_parent_box", null=True, blank=True)



class ConstantConfig(BaseModel):
    GAME_STATUS = [
        (0, "Night"),
        (1, "Day")
    ]
    game_current_state = models.IntegerField(choices=GAME_STATUS)
    wallet_init_value = models.IntegerField()
    question_level_0_value = models.IntegerField()
    question_level_1_value = models.IntegerField()
    question_level_2_value = models.IntegerField()
    question_solve_interest_percent = models.PositiveIntegerField()
    bought_question_max = models.PositiveIntegerField()
    contract_tax = models.PositiveIntegerField()
    inflation_coefficient = models.IntegerField()
    delay_factor = models.FloatField()
    question_level_0_max_try = models.PositiveIntegerField()
    question_level_1_max_try = models.PositiveIntegerField()
    question_level_2_max_try = models.PositiveIntegerField()
    question_code_max_try = models.IntegerField()
    question_level_0_early_solve_time = models.PositiveIntegerField()
    question_level_1_early_solve_time = models.PositiveIntegerField()
    question_level_2_early_solve_time = models.PositiveIntegerField()
    deposit_interest_percent = models.PositiveIntegerField()
    deposit_interest_day_time = models.PositiveIntegerField()
    deposit_interest_night_time = models.PositiveIntegerField()
    loan_interest_percent = models.PositiveIntegerField()
    loan_interest_day_time = models.PositiveIntegerField()
    loan_interest_night_time = models.PositiveIntegerField()
    bonus_percent = models.PositiveIntegerField()
    penaly_percent = models.PositiveIntegerField()
    subsidy_percentage = models.PositiveIntegerField()
    mafia_prison_per_report_time = models.PositiveIntegerField()
    assassination_attempt_cooldown_time = models.PositiveIntegerField()
    team_bank_transaction_cooldown = models.PositiveIntegerField()
    team_total_bank_value = models.PositiveIntegerField()
    team_loan_percent_max = models.PositiveIntegerField()
    team_escape_room_max = models.PositiveIntegerField()
    bank_robbery_contract_sponsorship_max = models.PositiveIntegerField()
    police_sensor_contract_sponsorship_max = models.PositiveIntegerField()
    escape_room_solve_time = models.PositiveIntegerField()


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
                                          on_delete=models.CASCADE,
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
    mafia_last_night_report = models.IntegerField()
    mafia_opened_night_escape_rooms = models.IntegerField()
    police_opened_night_escape_rooms = models.IntegerField()
    police_sensor_request_contracts = models.IntegerField()
    police_in_analysis_boxes = models.IntegerField()
    citizen_opened_night_escape_rooms = models.IntegerField()
    citizen_theft_request_contracts = models.IntegerField()

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
    body = models.TextField()
    qtype = models.IntegerField(choices=TYPE_CHOICE)
    answer_text = models.TextField(blank=True, null=True)
    answer_file = models.FileField(blank=True, null=True, upload_to='question_answer_file')
    no_valid_tries = models.IntegerField()
    valid_solve_minutes = models.IntegerField()


    def __str__(self) -> str:
        return f"{self.title}"

    


class TeamQuestionRel(BaseModel):
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='teamquestionrel_team')
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name='teamquestionrel_question')
    solved = models.BooleanField(default=False)
    received_score = models.IntegerField(default=0)
    tries = models.IntegerField(default=0)


class EscapeRoom(BaseModel):
    no_valid_citizen = models.IntegerField()
    no_valid_police = models.IntegerField()
    no_valid_mafia = models.IntegerField()
    bank_deposit_box = models.ForeignKey("BankDepositBox", on_delete=models.CASCADE, related_name='escaperoom_bank_deposit_box')


class Contract(BaseModel):
    STATE_CHOICE = [
        (0, 'waiting for sign'),
        (1, 'waiting to be done'),
        (2, 'archived')
    ]
    class CONTRACT_TYPES(models.TextChoices):
        question_ownership_transfer = 'question_ownership_transfer', _('Question Ownership Transfer'),
        bank_rubbery_sponsorship = 'bank_rubbery_sponsorship', _('Bank Robbery Sponsorship'),
        bank_sensor_installation_sponsorship = 'bank_sensor_installation_sponsorship', _('Bank Sensor Installation Sponsorship'),
        bodyguard_for_the_homeless = 'bodyguard_for_the_homeless', _('Bodyguard for the Homeless'),
        other = 'other', _('Other'),
    
    state = models.IntegerField(choices=STATE_CHOICE)
    contract_type = models.CharField(max_length=40, choices=CONTRACT_TYPES.choices)
    first_party = models.ForeignKey("Player", on_delete=models.CASCADE, related_name='contract_first_party')
    second_party = models.ForeignKey("Player", on_delete=models.CASCADE, related_name='contract_second_party', null=True)
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