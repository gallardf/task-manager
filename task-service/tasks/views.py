from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

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


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task CRUD operations.
    Permission checking uses the User model's permissions property.
    """
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
