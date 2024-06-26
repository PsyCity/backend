from django.contrib import admin
from . import models


class QuestionAdmin(admin.ModelAdmin): # new
     readonly_fields = ['body_preview']


@admin.register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ( "name", "team_role", "total_asset") 

admin.site.register(models.WarehouseBox)
admin.site.register(models.BankDepositBox)
admin.site.register(models.ConstantConfig)
admin.site.register(models.Player)
# admin.site.register(models.Team)
admin.site.register(models.TeamFeature)
admin.site.register(models.TeamQuestionRel)
admin.site.register(models.QuesionSolveTries)
admin.site.register(models.EscapeRoom)
admin.site.register(models.Contract)
admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.TeamJoinRequest)
admin.site.register(models.PlayerRole)
admin.site.register(models.BankRobbery)
admin.site.register(models.WarehouseQuestions)
admin.site.register(models.BankSensorInstall)
admin.site.register(models.Report)
admin.site.register(models.MoneyChangeLogger)