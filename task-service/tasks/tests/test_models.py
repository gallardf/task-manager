from django.test import TestCase

from tasks.models import Task, TaskStatus, Priority


class TaskModelTest(TestCase):
    """Tests for the Task model."""

    def test_create_task_with_defaults(self):
        """Task should be created with default status and priority."""
        task = Task.objects.create(
            title="Test task",
            created_by=1,
        )
        self.assertEqual(task.title, "Test task")
        self.assertEqual(task.status, TaskStatus.TODO)
        self.assertEqual(task.priority, Priority.MEDIUM)
        self.assertEqual(task.created_by, 1)
        self.assertIsNone(task.assigned_to)
        self.assertIsNone(task.due_date)
        self.assertEqual(task.description, "")

    def test_create_task_with_all_fields(self):
        """Task should store all provided fields."""
        task = Task.objects.create(
            title="Full task",
            description="A detailed description",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.HIGH,
            assigned_to=2,
            created_by=1,
            due_date="2026-12-31",
        )
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS)
        self.assertEqual(task.priority, Priority.HIGH)
        self.assertEqual(task.assigned_to, 2)
        self.assertEqual(str(task.due_date), "2026-12-31")

    def test_string_representation(self):
        """__str__ should return the task title."""
        task = Task(title="My Task")
        self.assertEqual(str(task), "My Task")

    def test_ordering(self):
        """Tasks should be ordered by -created_at by default."""
        task1 = Task.objects.create(title="First", created_by=1)
        task2 = Task.objects.create(title="Second", created_by=1)
        tasks = list(Task.objects.all())
        self.assertEqual(tasks[0], task2)
        self.assertEqual(tasks[1], task1)

    def test_task_status_choices(self):
        """TaskStatus should have the expected choices."""
        values = [c[0] for c in TaskStatus.choices]
        self.assertIn("todo", values)
        self.assertIn("in_progress", values)
        self.assertIn("done", values)
        self.assertIn("cancelled", values)

    def test_priority_choices(self):
        """Priority should have the expected choices."""
        values = [c[0] for c in Priority.choices]
        self.assertIn("low", values)
        self.assertIn("medium", values)
        self.assertIn("high", values)
        self.assertIn("urgent", values)
