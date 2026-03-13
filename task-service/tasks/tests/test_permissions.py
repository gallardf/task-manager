from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from tasks.models import Task
from users.models import Permission, Role, User


class PermissionTest(TestCase):
    """Tests for permission checking in task views."""

    def setUp(self):
        self.client = APIClient()

        # Create permissions
        self.perms = {}
        for codename in ["task:create", "task:read", "task:update", "task:delete"]:
            self.perms[codename] = Permission.objects.create(codename=codename)

        Task.objects.create(title="Test task", created_by=1)

    def _create_user_with_perms(self, username, perm_codenames):
        role = Role.objects.create(name=f"role_{username}")
        role.permissions.set([self.perms[c] for c in perm_codenames])
        user = User.objects.create_user(username=username, password="testpass", role=role)
        url = reverse("login")
        response = self.client.post(url, {"username": username, "password": "testpass"})
        return response.data["access"]

    def _auth(self, token):
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_read_permission_allows_get(self):
        """User with task:read permission can GET tasks."""
        token = self._create_user_with_perms("reader", ["task:read"])
        response = self.client.get("/api/tasks/", **self._auth(token))
        self.assertEqual(response.status_code, 200)

    def test_no_read_permission_denies_get(self):
        """User without task:read permission cannot GET tasks."""
        token = self._create_user_with_perms("noreader", [])
        response = self.client.get("/api/tasks/", **self._auth(token))
        self.assertEqual(response.status_code, 403)

    def test_no_create_permission_denies_post(self):
        """User without task:create permission cannot POST tasks."""
        token = self._create_user_with_perms("nocreator", ["task:read"])
        response = self.client.post(
            "/api/tasks/",
            {"title": "Denied task"},
            format="json",
            **self._auth(token),
        )
        self.assertEqual(response.status_code, 403)

    def test_create_permission_allows_post(self):
        """User with task:create permission can POST tasks."""
        token = self._create_user_with_perms("creator", ["task:create"])
        response = self.client.post(
            "/api/tasks/",
            {"title": "Allowed task", "assigned_to": 1},
            format="json",
            **self._auth(token),
        )
        self.assertEqual(response.status_code, 201)

    def test_no_update_permission_denies_patch(self):
        """User without task:update permission cannot PATCH tasks."""
        token = self._create_user_with_perms("noupdater", ["task:read"])
        task = Task.objects.first()
        response = self.client.patch(
            f"/api/tasks/{task.id}/",
            {"title": "Updated"},
            format="json",
            **self._auth(token),
        )
        self.assertEqual(response.status_code, 403)

    def test_no_delete_permission_denies_delete(self):
        """User without task:delete permission cannot DELETE tasks."""
        token = self._create_user_with_perms("nodeleter", ["task:read"])
        task = Task.objects.first()
        response = self.client.delete(
            f"/api/tasks/{task.id}/",
            **self._auth(token),
        )
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_returns_401(self):
        """Request without token should return 401."""
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, 401)

    def test_invalid_token_returns_401(self):
        """Invalid token should return 401."""
        response = self.client.get(
            "/api/tasks/",
            **self._auth("invalid-token-value"),
        )
        self.assertEqual(response.status_code, 401)
