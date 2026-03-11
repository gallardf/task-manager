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


class Task(models.Model):
    """Task model. References users by ID from the auth-service (no FK)."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.TODO,
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    assigned_to = models.IntegerField(null=True, blank=True, db_index=True)
    created_by = models.IntegerField(db_index=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["assigned_to", "status"]),
        ]

    def __str__(self):
        return self.title
