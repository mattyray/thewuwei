from datetime import date

from rest_framework import serializers

from .models import DailyCheckin, GratitudeEntry, JournalEntry


class JournalEntrySerializer(serializers.ModelSerializer):
    date = serializers.DateField(required=False, default=None)

    class Meta:
        model = JournalEntry
        fields = [
            "id",
            "content",
            "reflection",
            "date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "reflection", "created_at", "updated_at"]

    def create(self, validated_data):
        if validated_data.get("date") is None:
            validated_data["date"] = date.today()
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class DailyCheckinSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyCheckin
        fields = [
            "id",
            "date",
            "meditation_completed",
            "meditation_duration",
            "meditation_completed_at",
            "gratitude_completed",
            "gratitude_completed_at",
            "journal_completed",
            "journal_completed_at",
        ]
        read_only_fields = ["id"]


class GratitudeEntrySerializer(serializers.ModelSerializer):
    date = serializers.DateField(required=False, default=None)

    class Meta:
        model = GratitudeEntry
        fields = ["id", "date", "items", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        if validated_data.get("date") is None:
            validated_data["date"] = date.today()
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
