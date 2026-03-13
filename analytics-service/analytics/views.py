from datetime import date

from django.db.models import Count
from rest_framework import serializers as drf_serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from tasks.models import Task, TaskStatus, User
from .serializers import StatusSummarySerializer, UserSummarySerializer


class TaskSerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


@extend_schema(tags=["Analytics"])
class SummaryView(APIView):
    """Nombre de tâches groupées par statut (todo, in_progress, done, cancelled)."""
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Résumé par statut",
        responses={200: StatusSummarySerializer(many=True)},
    )
    def get(self, request):
        if "analytics:read" not in getattr(request, "user_permissions", []):
            raise PermissionDenied(detail="Permission 'analytics:read' requise.")

        data = Task.objects.values("status").annotate(count=Count("id"))
        serializer = StatusSummarySerializer(data, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Analytics"])
class ByUserView(APIView):
    """Nombre de tâches groupées par utilisateur assigné."""
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Tâches par utilisateur",
        responses={200: UserSummarySerializer(many=True)},
    )
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


@extend_schema(tags=["Analytics"])
class OverdueView(APIView):
    """Liste des tâches en retard (date d'échéance dépassée, ni terminées ni annulées)."""
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Tâches en retard",
        responses={200: TaskSerializer(many=True)},
    )
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
