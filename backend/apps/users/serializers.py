from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "timezone",
            "daily_reminder_time",
            "reminder_enabled",
            "reflections_today",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "reflections_today", "date_joined"]
