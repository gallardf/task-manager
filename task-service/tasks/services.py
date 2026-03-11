from django.db import models

from .models import Task


class TaskService:
    """Encapsulates task business logic, separated from views."""

    @staticmethod
    def create_task(data: dict, user_id: int) -> Task:
        """Create a task, automatically setting created_by."""
        data["created_by"] = user_id
        return Task.objects.create(**data)

    @staticmethod
    def can_modify_task(task: Task, user) -> bool:
        """
        Check if a user can modify/delete a task.
        Admins and managers can modify any task.
        Members can only modify tasks they created or are assigned to.
        """
        role = user.role.name if user.role else None
        if role in ("admin", "manager"):
            return True
        return task.created_by == user.id or task.assigned_to == user.id

    @staticmethod
    def get_user_tasks(user_id: int):
        """Get tasks created by or assigned to a user."""
        return Task.objects.filter(
            models.Q(created_by=user_id) | models.Q(assigned_to=user_id)
        )
