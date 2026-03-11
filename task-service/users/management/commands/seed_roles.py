from django.core.management.base import BaseCommand

from users.models import Permission, Role, User


class Command(BaseCommand):
    help = "Seed roles and permissions"

    def handle(self, *args, **options):
        # --- Permissions ---
        permission_codenames = [
            ("user:create", "Create users"),
            ("user:read", "Read users"),
            ("user:update", "Update users"),
            ("user:delete", "Delete users"),
            ("task:create", "Create tasks"),
            ("task:read", "Read tasks"),
            ("task:update", "Update tasks"),
            ("task:delete", "Delete tasks"),
            ("analytics:read", "Read analytics"),
        ]

        permissions = {}
        for codename, description in permission_codenames:
            perm, created = Permission.objects.get_or_create(
                codename=codename,
                defaults={"description": description},
            )
            permissions[codename] = perm
            if created:
                self.stdout.write(f"  Created permission: {codename}")

        # --- Roles ---
        role_definitions = {
            "admin": list(permissions.keys()),
            "manager": ["task:create", "task:read", "task:update", "task:delete", "analytics:read", "users.read"],
            "member": ["task:create", "task:read", "task:update", "analytics:read", "users.read"],
            "viewer": ["task:read", "analytics:read"],
        }

        for role_name, perm_codenames in role_definitions.items():
            role, created = Role.objects.get_or_create(name=role_name)
            role.permissions.set([permissions[c] for c in perm_codenames])
            if created:
                self.stdout.write(f"  Created role: {role_name}")

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
