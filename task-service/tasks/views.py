from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema, extend_schema_view

from .filters import TaskFilter
from .models import Task
from .serializers import TaskSerializer
from .services import TaskService


PERMISSION_MAP = {
    "GET": "task:read",
    "HEAD": "task:read",
    "OPTIONS": "task:read",
    "POST": "task:create",
    "PUT": "task:update",
    "PATCH": "task:update",
    "DELETE": "task:delete",
}


@extend_schema_view(
    list=extend_schema(summary="Lister les tâches", description="Liste paginée avec filtres (status, priority, assigned_to, created_by, due_date). Requiert la permission `task:read`.", tags=["Tasks"]),
    create=extend_schema(summary="Créer une tâche", description="Requiert la permission `task:create`. Le champ `created_by` est rempli automatiquement.", tags=["Tasks"]),
    retrieve=extend_schema(summary="Détail d'une tâche", tags=["Tasks"]),
    update=extend_schema(summary="Modifier une tâche", description="Admin/manager : toute tâche. Member : uniquement ses tâches ou celles qui lui sont assignées.", tags=["Tasks"]),
    partial_update=extend_schema(summary="Modifier partiellement une tâche", tags=["Tasks"]),
    destroy=extend_schema(summary="Supprimer une tâche", description="Mêmes règles que la modification.", tags=["Tasks"]),
)
class TaskViewSet(viewsets.ModelViewSet):
    """CRUD des tâches avec contrôle de permissions basé sur le rôle."""
    serializer_class = TaskSerializer
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "due_date", "priority", "status"]

    def get_queryset(self):
        return Task.objects.all()

    def check_permissions(self, request):
        super().check_permissions(request)
        required_permission = PERMISSION_MAP.get(request.method)
        if required_permission and required_permission not in request.user.permissions:
            raise PermissionDenied(
                detail=f"Permission '{required_permission}' requise."
            )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.id)

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        if not TaskService.can_modify_task(task, request.user):
            raise PermissionDenied(
                detail="Vous ne pouvez pas modifier cette tâche."
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        if not TaskService.can_modify_task(task, request.user):
            raise PermissionDenied(
                detail="Vous ne pouvez pas supprimer cette tâche."
            )
        return super().destroy(request, *args, **kwargs)
