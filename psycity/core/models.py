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
    unlocker_id = models.ForeignKey("Player", on_delete=models.CASCADE, related_name='warehouse_box_unlocker')
    sensor_state = models.BooleanField(default=False)
    sensor_hacker = models.ForeignKey("Player", on_delete=models.CASCADE, related_name='warehouse_box_sensor_hacker')
    expiration_date = models.DateTimeField(auto_now_add=False)
    question_id = models.ForeignKey("Question", on_delete=models.CASCADE, related_name='warehouse_box_question')
    money = models.PositiveIntegerField()


class BankDepositBox(BaseModel):
    SENSOR_STATE_CHOICE = [
        (1, 'Installed'),
        (2, 'Not Installed'),
    ]
    money = models.PositiveIntegerField()
    robbery_state = models.BooleanField(default=False)
    rubbery_team_id = models.ForeignKey("Team", on_delete=models.CASCADE, related_name="bankdispositbox_rubbery_team")
    sensor_state = models.CharField(max_length=30, choices=SENSOR_STATE_CHOICE)
    sensor_owner_id = models.ForeignKey("Team", on_delete=models.CASCADE, related_name="bankdispositbox_sensor_owner")
    is_copy = models.BooleanField(default=False)
    parent_box_id = models.ForeignKey('self', on_delete=models.CASCADE, related_name="bankdispositbox_parent_box", null=True, blank=True)



class ConstantConfig(BaseModel):
    GAME_STATUS = [
        (0, "Night"),
        (1, "Day")
    ]
    team_member_min = models.PositiveIntegerField()
    team_member_max = models.PositiveIntegerField()
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
    ROLES_CHOICES = [
        ('Nerd', 'Nerd'),
        ('MasterMind', 'Master mind'),
        ('SmoothTalker', 'Smooth Talker'),
    ]

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
    player_role = models.CharField(max_length=20, choices=ROLES_CHOICES)
    team_id = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='player_team')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    wallet = models.IntegerField()
    bank_liabilities = models.IntegerField()
    last_assassination_attempt = models.DateTimeField() # todo
    bodyguard_team_id = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='player_bodyguard_team')
    last_bodyguard_cost = models.IntegerField()

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
    wallet = models.IntegerField()
    bank = models.IntegerField()
    total_asset = models.IntegerField()
    level = models.PositiveIntegerField(validators=[
            MinValueValidator(0, message='Value must be greater than or equal to 0.'),
            MaxValueValidator(10, message='Value must be less than or equal to 10.'),
        ])
    bank_liabilities = models.IntegerField()
    max_bank_loan = models.IntegerField()
    last_bank_action = models.DateTimeField()
    today_bought_question = models.IntegerField()

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
    last_owner_id = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='question_last_owner_id')
    price = models.IntegerField()
    score = models.IntegerField()
    is_published = models.BooleanField(default=False)
    title = models.CharField(max_length=300)
    body = models.TextField()
    qtype = models.CharField(max_length=30, choices=TYPE_CHOICE)
    answer = models.TextField()
    no_valid_tries = models.IntegerField()
    valid_solve_minutes = models.IntegerField()

    


class TeamQuestionRel(BaseModel):
    team_id = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='teamquestionrel_team')
    question_id = models.ForeignKey("Question", on_delete=models.CASCADE, related_name='teamquestionrel_question')
    solved = models.BooleanField()
    received_score = models.IntegerField()
    tries = models.IntegerField()


class EscapeRoom(BaseModel):
    no_valid_citizen = models.IntegerField()
    no_valid_police = models.IntegerField()
    no_valid_mafia = models.IntegerField()
    bank_deposit_box_id = models.ForeignKey("BankDepositBox", on_delete=models.CASCADE, related_name='escaperoom_bank_deposit_box')


class Contract(BaseModel):
    STATE_CHOICE = [
        (0, 'waiting for sign'),
        (1, 'waiting to be done'),
        (2, 'archived')
    ]
    CONTRACT_TYPES = [
        ('A', 'Question Ownership Transfer'),
        ('B', 'Bank Robbery Sponsorship'),
        ('C', 'Bank Sensor Installation Sponsorship'),
        ('D', 'Bodyguard for the Homeless'),
        ('E', 'Other'),
    ]
    state = models.IntegerField(choices=STATE_CHOICE)
    contract_type = models.CharField(max_length=1, choices=CONTRACT_TYPES)
    first_party_id = models.ForeignKey("Player", on_delete=models.CASCADE, related_name='contract_first_party')
    first_second_id = models.ForeignKey("Player", on_delete=models.CASCADE, related_name='contract_second_party')
    terms = models.TextField()
    first_party_agree = models.BooleanField()
    second_party_agree = models.BooleanField()
    archive = models.BooleanField() # todo isn't it avail in state?

