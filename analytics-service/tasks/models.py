from django.db import models


class TaskStatus(models.TextChoices):
    TODO = "todo", "À faire"
    IN_PROGRESS = "in_progress", "En cours"
    DONE = "done", "Terminée"
    CANCELLED = "cancelled", "Annulée"


class Priority(models.TextChoices):
    LOW = "low", "Basse"
    MEDIUM = "medium", "Moyenne"
    HIGH = "high", "Haute"
    URGENT = "urgent", "Urgente"


class User(models.Model):
    """Read-only mirror of the User model from task-service."""
    username = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = "users_user"

    def __str__(self):
        return self.username


class Task(models.Model):
    """Read-only mirror of the Task model from task-service. Schema managed by task-service."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.TODO)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    assigned_to = models.IntegerField(null=True, blank=True, db_index=True)
    created_by = models.IntegerField(db_index=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "tasks_task"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
