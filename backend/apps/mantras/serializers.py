from rest_framework import serializers

from .models import Mantra


class MantraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mantra
        fields = ["id", "content", "order", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ReorderSerializer(serializers.Serializer):
    order = serializers.ListField(child=serializers.IntegerField())
