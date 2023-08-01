from django.db import models
from django.utils.translation import gettext_lazy as _
# Create your models here.

class Warehouse(models.Model):
    SENSOR_STATES = HACKED, INTACT = "H", "I"

    # question_id = models.ForeignKey("Question", on_delete=models.DO_NOTHING)
    # unlocker_id = models.ForeignKey("Player", on_delete=models.DO_NOTHING)
    # sensor_hacker = models.ForeignKey("Player", on_delete=models.DO_NOTHING)
    money = models.PositiveIntegerField()

    is_lock = models.BinaryField(default=True)


    sensor_state = models.CharField(max_length=1,
                                    choices=SENSOR_STATES,
                                    default=INTACT)
    
    expiration_date = models.DateTimeField(auto_now=False, auto_now_add=False)
    create_date = models.DateTimeField(auto_now=True, auto_now_add=True)  #FIXME 
    write_date = models.DateTimeField(auto_now=True, auto_now_add=True)



