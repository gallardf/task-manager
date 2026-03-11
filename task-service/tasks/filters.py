import django_filters
from .models import Task


class TaskFilter(django_filters.FilterSet):
    """Filter tasks by status, priority, assignee, creator, and due date range."""
    due_date_before = django_filters.DateFilter(field_name="due_date", lookup_expr="lte")
    due_date_after = django_filters.DateFilter(field_name="due_date", lookup_expr="gte")

    class Meta:
        model = Task
        fields = ["status", "priority", "assigned_to", "created_by"]
