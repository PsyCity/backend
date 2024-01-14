from django.contrib import admin
from . import models


class QuestionAdmin(admin.ModelAdmin): # new
     readonly_fields = ['body_preview']

admin.site.register(models.WarehouseBox)
admin.site.register(models.BankDepositBox)
admin.site.register(models.ConstantConfig)
admin.site.register(models.Player)
admin.site.register(models.Team)
admin.site.register(models.TeamFeature)
admin.site.register(models.TeamQuestionRel)
admin.site.register(models.EscapeRoom)
admin.site.register(models.Contract)
admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.TeamJoinRequest)
admin.site.register(models.PlayerRole)
admin.site.register(models.BankRobbery)
admin.site.register(models.BankSensorInstall)

