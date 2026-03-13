from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from tasks.models import Task
from users.models import Permission, Role, User


class TaskViewSetTest(TestCase):
    """Tests for TaskViewSet CRUD operations."""

    def setUp(self):
        self.client = APIClient()

        # Create permissions
        perms = {}
        for codename in ["task:create", "task:read", "task:update", "task:delete", "analytics:read"]:
            perms[codename] = Permission.objects.create(codename=codename)

        # Create roles
        admin_role = Role.objects.create(name="admin")
        admin_role.permissions.set(perms.values())

        member_role = Role.objects.create(name="member")
        member_role.permissions.set([perms["task:create"], perms["task:read"], perms["task:update"], perms["task:delete"]])

        readonly_role = Role.objects.create(name="viewer")
        readonly_role.permissions.set([perms["task:read"]])

        # Create users
        self.admin_user = User.objects.create_user(username="admin", password="admin123", role=admin_role)
        self.member_user = User.objects.create_user(username="member", password="member123", role=member_role)
        self.readonly_user = User.objects.create_user(username="viewer", password="viewer123", role=readonly_role)

        # Get tokens
        self.admin_token = self._get_token("admin", "admin123")
        self.member_token = self._get_token("member", "member123")
        self.readonly_token = self._get_token("viewer", "viewer123")

        self.task = Task.objects.create(
            title="Existing task",
            description="A test task",
            created_by=self.admin_user.id,
        )

    def _get_token(self, username, password):
        url = reverse("login")
        response = self.client.post(url, {"username": username, "password": password})
        return response.data["access"]

    def _auth(self, token):
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    # --- Create ---
    def test_create_task_with_permission(self):
        """User with task:create permission can create a task."""
        response = self.client.post(
            "/api/tasks/",
            {"title": "New task", "description": "Description", "assigned_to": self.member_user.id},
            format="json",
            **self._auth(self.admin_token),
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "New task")
        self.assertEqual(response.data["created_by"], self.admin_user.id)

    def test_create_task_without_permission(self):
        """User without task:create permission cannot create a task."""
        response = self.client.post(
            "/api/tasks/",
            {"title": "New task"},
            format="json",
            **self._auth(self.readonly_token),
        )
        self.assertEqual(response.status_code, 403)

    def test_create_task_without_token(self):
        """Request without token returns 401."""
        response = self.client.post(
            "/api/tasks/",
            {"title": "New task"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    # --- List ---
    def test_list_tasks_with_permission(self):
        """User with task:read permission can list tasks."""
        response = self.client.get(
            "/api/tasks/",
            **self._auth(self.admin_token),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)

    # --- Retrieve ---
    def test_retrieve_task(self):
        """User with task:read permission can retrieve a single task."""
        response = self.client.get(
            f"/api/tasks/{self.task.id}/",
            **self._auth(self.admin_token),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Existing task")

    # --- Update ---
    def test_update_task_as_owner(self):
        """Owner can update their own task."""
        response = self.client.patch(
            f"/api/tasks/{self.task.id}/",
            {"title": "Updated task"},
            format="json",
            **self._auth(self.admin_token),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Updated task")

    def test_member_cannot_update_others_task(self):
        """Member cannot update a task they didn't create and aren't assigned to."""
        other_task = Task.objects.create(title="Other task", created_by=99)
        response = self.client.patch(
            f"/api/tasks/{other_task.id}/",
            {"title": "Hacked"},
            format="json",
            **self._auth(self.member_token),
        )
        self.assertEqual(response.status_code, 403)

    # --- Delete ---
    def test_admin_can_delete_any_task(self):
        """Admin can delete any task."""
        response = self.client.delete(
            f"/api/tasks/{self.task.id}/",
            **self._auth(self.admin_token),
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Task.objects.count(), 0)

    def test_member_cannot_delete_others_task(self):
        """Member cannot delete a task they didn't create."""
        other_task = Task.objects.create(title="Other task", created_by=99)
        response = self.client.delete(
            f"/api/tasks/{other_task.id}/",
            **self._auth(self.member_token),
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Task.objects.filter(id=other_task.id).exists())

    def test_member_can_delete_own_task(self):
        """Member can delete a task they created."""
        own_task = Task.objects.create(title="My task", created_by=self.member_user.id)
        response = self.client.delete(
            f"/api/tasks/{own_task.id}/",
            **self._auth(self.member_token),
        )
        self.assertEqual(response.status_code, 204)

    def test_assigned_member_can_update_task(self):
        """Member assigned to a task can update it."""
        assigned_task = Task.objects.create(
            title="Assigned task", created_by=99, assigned_to=self.member_user.id,
        )
        response = self.client.patch(
            f"/api/tasks/{assigned_task.id}/",
            {"title": "Updated by assignee"},
            format="json",
            **self._auth(self.member_token),
        )
        self.assertEqual(response.status_code, 200)
