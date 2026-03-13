from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import Permission, Role, User


class PermissionTests(APITestCase):
    def setUp(self):
        # Create permissions
        self.perms = {}
        for codename in ["user:create", "user:read", "user:update", "user:delete",
                         "task:create", "task:read", "task:update"]:
            self.perms[codename] = Permission.objects.create(codename=codename)

        # Create roles
        self.admin_role = Role.objects.create(name="admin")
        self.admin_role.permissions.set(self.perms.values())

        self.member_role = Role.objects.create(name="member")
        self.member_role.permissions.set([
            self.perms["task:create"],
            self.perms["task:read"],
            self.perms["task:update"],
        ])

        # Create users
        self.admin_user = User.objects.create_user(
            username="admin", password="admin123", role=self.admin_role,
        )
        self.member_user = User.objects.create_user(
            username="member", password="member123", role=self.member_role,
        )

    def _login(self, username, password):
        url = reverse("login")
        response = self.client.post(url, {"username": username, "password": password})
        return response.data["access"]

    def test_admin_can_list_users(self):
        token = self._login("admin", "admin123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_member_can_list_users(self):
        """Members can list users (needed for task assignment dropdown)."""
        token = self._login("member", "member123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_update_user_role(self):
        token = self._login("admin", "admin123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("user-detail", args=[self.member_user.id])
        response = self.client.patch(url, {"role": self.admin_role.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.member_user.refresh_from_db()
        self.assertEqual(self.member_user.role.name, "admin")

    def test_non_admin_cannot_update_users(self):
        token = self._login("member", "member123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("user-detail", args=[self.admin_user.id])
        response = self.client.patch(url, {"first_name": "Hacked"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
