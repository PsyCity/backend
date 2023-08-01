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
