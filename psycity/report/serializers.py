from rest_framework import serializers
from core.models import Report


class SimpleReportSerializer(
    serializers.ModelSerializer
    ):
    class Meta:
        model = Report
        fields = (
            "player_reporter",
            "description"
        )

    def create(self, validated_data):
        return super().create(validated_data)