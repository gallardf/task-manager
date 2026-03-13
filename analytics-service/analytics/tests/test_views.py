from datetime import date, timedelta, datetime

import jwt
from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient

from tasks.models import Task


def make_token(permissions=None, expired=False):
    """Generate a JWT token for testing."""
    payload = {
        "user_id": 1,
        "username": "testuser",
        "role": "admin",
        "permissions": permissions or [],
        "exp": datetime.utcnow() + timedelta(hours=-1 if expired else 1),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


class SummaryViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/analytics/summary/"
        self.token = make_token(["analytics:read"])

        Task.objects.create(title="Task 1", status="todo", created_by=1)
        Task.objects.create(title="Task 2", status="todo", created_by=1)
        Task.objects.create(title="Task 3", status="done", created_by=1)

    def test_summary_returns_count_by_status(self):
        response = self.client.get(self.url, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, 200)
        data = {item["status"]: item["count"] for item in response.data}
        self.assertEqual(data["todo"], 2)
        self.assertEqual(data["done"], 1)

    def test_summary_empty_database(self):
        Task.objects.all().delete()
        response = self.client.get(self.url, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])


class ByUserViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/analytics/by-user/"
        self.token = make_token(["analytics:read"])

        Task.objects.create(title="Task 1", assigned_to=1, created_by=1)
        Task.objects.create(title="Task 2", assigned_to=1, created_by=1)
        Task.objects.create(title="Task 3", assigned_to=2, created_by=1)
        Task.objects.create(title="Task 4", assigned_to=None, created_by=1)

    def test_by_user_returns_count_by_assigned_to(self):
        response = self.client.get(self.url, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)  # user 1, user 2, unassigned

    def test_by_user_includes_unassigned(self):
        response = self.client.get(self.url, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        unassigned = [item for item in response.data if item["username"] is None]
        self.assertEqual(len(unassigned), 1)
        self.assertEqual(unassigned[0]["count"], 1)


class OverdueViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/analytics/overdue/"
        self.token = make_token(["analytics:read"])

        yesterday = date.today() - timedelta(days=1)
        tomorrow = date.today() + timedelta(days=1)

        # Overdue: past due date + not done/cancelled
        Task.objects.create(title="Overdue 1", due_date=yesterday, status="todo", created_by=1)
        Task.objects.create(title="Overdue 2", due_date=yesterday, status="in_progress", created_by=1)
        # Not overdue: past due date but done
        Task.objects.create(title="Done", due_date=yesterday, status="done", created_by=1)
        # Not overdue: past due date but cancelled
        Task.objects.create(title="Cancelled", due_date=yesterday, status="cancelled", created_by=1)
        # Not overdue: future due date
        Task.objects.create(title="Future", due_date=tomorrow, status="todo", created_by=1)
        # Not overdue: no due date
        Task.objects.create(title="No date", status="todo", created_by=1)

    def test_overdue_returns_only_overdue_tasks(self):
        response = self.client.get(self.url, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, 200)
        titles = [task["title"] for task in response.data]
        self.assertIn("Overdue 1", titles)
        self.assertIn("Overdue 2", titles)
        self.assertEqual(len(titles), 2)

    def test_overdue_excludes_done_and_cancelled(self):
        response = self.client.get(self.url, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        titles = [task["title"] for task in response.data]
        self.assertNotIn("Done", titles)
        self.assertNotIn("Cancelled", titles)


class AnalyticsAuthTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.urls = [
            "/api/analytics/summary/",
            "/api/analytics/by-user/",
            "/api/analytics/overdue/",
        ]

    def test_no_token_returns_401(self):
        for url in self.urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 401, f"Expected 401 for {url}")

    def test_invalid_token_returns_401(self):
        for url in self.urls:
            response = self.client.get(url, HTTP_AUTHORIZATION="Bearer invalid-token")
            self.assertEqual(response.status_code, 401, f"Expected 401 for {url}")

    def test_expired_token_returns_401(self):
        token = make_token(["analytics:read"], expired=True)
        for url in self.urls:
            response = self.client.get(url, HTTP_AUTHORIZATION=f"Bearer {token}")
            self.assertEqual(response.status_code, 401, f"Expected 401 for {url}")

    def test_missing_permission_returns_403(self):
        token = make_token(["task:read"])  # has a token but not analytics:read
        for url in self.urls:
            response = self.client.get(url, HTTP_AUTHORIZATION=f"Bearer {token}")
            self.assertEqual(response.status_code, 403, f"Expected 403 for {url}")
