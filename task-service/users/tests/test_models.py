from django.test import TestCase

from users.models import Permission, Role, User


class UserModelTest(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name="member")
        self.perm = Permission.objects.create(codename="task:read", description="Read tasks")
        self.role.permissions.add(self.perm)

    def test_create_user_with_username(self):
        user = User.objects.create_user(username="testuser", password="pass1234")
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("pass1234"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_string_representation(self):
        user = User.objects.create_user(username="testuser", password="pass1234")
        self.assertEqual(str(user), "testuser")

    def test_user_permissions_with_role(self):
        user = User.objects.create_user(username="permuser", password="pass1234", role=self.role)
        self.assertIn("task:read", user.permissions)

    def test_user_permissions_without_role(self):
        user = User.objects.create_user(username="norole", password="pass1234")
        self.assertEqual(user.permissions, [])

    def test_create_user_without_username_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(username="", password="pass1234")
