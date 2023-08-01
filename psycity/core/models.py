from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Player(models.Model):
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    wallet = models.IntegerField()
    bank_liabilities = models.IntegerField()
    last_assassination_attempt = models.DateTimeField() # todo
    last_bodyguard_cost = models.IntegerField()

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Team(models.Model):
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

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TeamFeature(models.Model):
    mafia_last_night_report = models.IntegerField()
    mafia_opened_night_escape_rooms = models.IntegerField()
    police_opened_night_escape_rooms = models.IntegerField()
    police_sensor_request_contracts = models.IntegerField()
    police_in_analysis_boxes = models.IntegerField()
    citizen_opened_night_escape_rooms = models.IntegerField()
    citizen_theft_request_contracts = models.IntegerField()

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class TeamQuestionRel(models.Model):
    solved = models.IntegerField()
    received_score = models.IntegerField()
    tries = models.IntegerField()

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class EscapeRoom(models.Model):
    no_valid_citizen = models.IntegerField()
    no_valid_police = models.IntegerField()
    bank_deposit_box_id = models.IntegerField()

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class Contract(models.Model):
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
    terms = models.TextField()
    first_party_agree = models.BooleanField()
    second_party_agree = models.BooleanField()
    archive = models.BooleanField() # todo isn't it avail in state?

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

