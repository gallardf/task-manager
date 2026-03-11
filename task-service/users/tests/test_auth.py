from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import Permission, Role, User


class AuthTests(APITestCase):
    def setUp(self):
        self.member_role = Role.objects.create(name="member")
        perm = Permission.objects.create(codename="task:read")
        self.member_role.permissions.add(perm)

        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            role=self.member_role,
        )

    def test_login_returns_tokens(self):
        url = reverse("login")
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password_returns_401(self):
        url = reverse("login")
        data = {"username": "testuser", "password": "wrongpass"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_authenticated_user(self):
        login_url = reverse("login")
        login_response = self.client.post(login_url, {
            "username": "testuser",
            "password": "testpass123",
        })
        token = login_response.data["access"]

        me_url = reverse("me")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")

    def test_me_returns_401_without_token(self):
        url = reverse("me")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_works(self):
        login_url = reverse("login")
        login_response = self.client.post(login_url, {
            "username": "testuser",
            "password": "testpass123",
        })
        refresh_token = login_response.data["refresh"]

        refresh_url = reverse("token-refresh")
        response = self.client.post(refresh_url, {"refresh": refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
