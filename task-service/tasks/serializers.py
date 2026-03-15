from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model."""
    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "status", "priority",
            "assigned_to", "created_by", "due_date",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]
