from django.contrib import admin
from . import models

admin.site.register(models.WarehouseBox)
admin.site.register(models.BankDepositBox)
admin.site.register(models.ConstantConfig)
admin.site.register(models.Player)
admin.site.register(models.Team)
admin.site.register(models.TeamFeature)
admin.site.register(models.TeamQuestionRel)
admin.site.register(models.EscapeRoom)
admin.site.register(models.Contract)
admin.site.register(models.Question)
admin.site.register(models.TeamJoinRequest)
admin.site.register(models.PlayerRole)