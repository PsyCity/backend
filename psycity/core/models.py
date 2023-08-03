from django.db import models
from django.utils.translation import gettext_lazy as _
# Create your models here.

class Warehouse(models.Model):
    
    # question_id = models.ForeignKey("Question", on_delete=models.DO_NOTHING)
    # unlocker_id = models.ForeignKey("Player", on_delete=models.DO_NOTHING)
    # sensor_hacker = models.ForeignKey("Player", on_delete=models.DO_NOTHING)
    money = models.PositiveIntegerField()
    is_lock = models.BinaryField(default=True)
    sensor_state = models.BooleanField(defualt=False)
    expiration_date = models.DateTimeField(auto_now=False, auto_now_add=False)
    create_date = models.DateTimeField(auto_now=True, auto_now_add=True)  #FIXME 
    write_date = models.DateTimeField(auto_now=True, auto_now_add=True)


class BankDeposit(models.model):
    money = models.PositiveIntegerField()
    robbery_state = models.BooleanField(default=False)
    # rubbery_team = models.ForeignKey("Team", on_delete=models.DO_NOTHING, related_name="bank_robberies")
    sensor_state = models.BooleanField(default=False)
    # sensor_owner = models.ForeignKey("Team", on_delete=models.DO_NOTHING, related_name="bank_sensor")
    is_copy = models.BooleanField(default=False)
    parent_box = models.ForeignKey("BankDeposit", on_delete=models.DO_NOTHING, related_name="childe_box")
    create_date = models.DateTimeField(auto_now=True, auto_now_add=True)  #FIXME 
    write_date = models.DateTimeField(auto_now=True, auto_now_add=True)


class EscapeRoom(models.Model):
    no_valid_citizen = models.PositiveIntegerField()
    no_valid_police = models.PositiveIntegerField()
    no_valid_mafia = models.PositiveIntegerField()
    bank_deposit_box = models.ForeignKey(BankDeposit, related_name="escape_rooms", on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now=True, auto_now_add=True)  #FIXME 
    write_date = models.DateTimeField(auto_now=True, auto_now_add=True)


class Contract(models.Model):

    CONTRACT_TYPE = [
        ("R", "Bank_Robbery"),
        ("S", "Sensor_Installation"),
        ("B", "Bodyguard"),
        ("D", "Dealing"),
        ("O", "Other")
    ]

    contract_type = models.CharField(max_length=1,
                                     choices=CONTRACT_TYPE)
    state = models.IntegerField()
    terms = models.TextField()
    archive = models.TextField()
    # first_party_id = 
    # second_party_id
    first_party_agree = models.BooleanField(null=True, blank=True)
    second_party_agree = models.BooleanField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now=True, auto_now_add=True)
    write_date  = models.DateTimeField(auto_now=True, auto_now_add=True)


class ConstantConfig(models.Model):
    team_member_min = models.PositiveIntegerField()
    team_member_max = models.PositiveIntegerField()
    game_current_state = models.IntegerField(_("current_game_state"), choices=("DAY NIGHT"))
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
    question_code_max_try = models.BigIntegerField()
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


