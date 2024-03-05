from rest_framework import serializers
from core.models import Report, Contract, Team
from rest_framework import exceptions

class SimpleReportSerializer(
    serializers.ModelSerializer
    ):
    class Meta:
        model = Report
        fields = (
            "player_reporter",
            "description"
        )


class ContractReportSerializer(
    serializers.ModelSerializer
    ):

    class Meta:
        model = Report
        fields = (
            "contract",
            "description",
            "team_reporter"
        )

    def validate_contract(self, obj: Contract):
        if not (
            (obj.state == 2) and\
            obj.first_party_agree and\
            obj.second_party_agree 
            ):
            raise exceptions.ValidationError(
                "gharardad dar state eshtebah ya emza nashodeh."
            )
        return obj
    
    def is_valid(self, *, raise_exception=False):
        return super().is_valid(raise_exception=raise_exception)
    
    def is_acceptable(self):
        contract :Contract = self.validated_data["contract"]
        reporter : Team = self.validated_data["team_reporter"]
        l = []
        if contract.first_party_team: l.append(contract.first_party_team.pk)
        if contract.second_party_team: l.append(contract.second_party_team.pk)
        if reporter.pk not in l:
            raise exceptions.NotAcceptable(
                "team dar gharadad nist."
            )