from rest_framework import serializers

from .models import Todo


class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = [
            "id",
            "task",
            "due_date",
            "completed",
            "completed_at",
            "created_at",
        ]
        read_only_fields = ["id", "completed", "completed_at", "created_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
