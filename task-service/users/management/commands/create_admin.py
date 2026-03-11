import os

from django.core.management.base import BaseCommand

from users.models import Role, User


class Command(BaseCommand):
    help = "Create an admin user"

    def add_arguments(self, parser):
        parser.add_argument("--username", default=os.environ.get("ADMIN_USERNAME"))
        parser.add_argument("--password", default=os.environ.get("ADMIN_PASSWORD"))

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]

        if not username or not password:
            self.stderr.write("--username and --password are required (or set ADMIN_USERNAME/ADMIN_PASSWORD env vars).")
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Admin user {username} already exists, skipping.")
            return

        admin_role = Role.objects.filter(name="admin").first()
        if not admin_role:
            self.stderr.write("Role 'admin' not found. Run seed_roles first.")
            return

        User.objects.create_user(
            username=username,
            password=password,
            role=admin_role,
        )
        self.stdout.write(self.style.SUCCESS(f"Admin user {username} created."))
