from datetime import date

from django.db.models import Count
from rest_framework import serializers as drf_serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks.models import Task, TaskStatus, User
from .serializers import StatusSummarySerializer, UserSummarySerializer


class TaskSerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class SummaryView(APIView):
    """GET: task count grouped by status."""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        if "analytics:read" not in getattr(request, "user_permissions", []):
            raise PermissionDenied(detail="Permission 'analytics:read' requise.")

        data = Task.objects.values("status").annotate(count=Count("id"))
        serializer = StatusSummarySerializer(data, many=True)
        return Response(serializer.data)


class ByUserView(APIView):
    """GET: task count grouped by assigned_to user."""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        if "analytics:read" not in getattr(request, "user_permissions", []):
            raise PermissionDenied(detail="Permission 'analytics:read' requise.")

        data = Task.objects.values("assigned_to").annotate(count=Count("id"))
        # Resolve user IDs to usernames
        user_ids = [item["assigned_to"] for item in data if item["assigned_to"] is not None]
        usernames = dict(User.objects.filter(id__in=user_ids).values_list("id", "username"))
        result = [
            {
                "username": usernames.get(item["assigned_to"], "Non assigné") if item["assigned_to"] else None,
                "count": item["count"],
            }
            for item in data
        ]
        serializer = UserSummarySerializer(result, many=True)
        return Response(serializer.data)


class OverdueView(APIView):
    """GET: list of overdue tasks (due_date < today, not done/cancelled)."""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        if "analytics:read" not in getattr(request, "user_permissions", []):
            raise PermissionDenied(detail="Permission 'analytics:read' requise.")

        overdue_tasks = Task.objects.filter(
            due_date__lt=date.today(),
        ).exclude(
            status__in=[TaskStatus.DONE, TaskStatus.CANCELLED],
        )
        serializer = TaskSerializer(overdue_tasks, many=True)
        return Response(serializer.data)
