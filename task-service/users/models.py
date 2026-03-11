from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class Permission(models.Model):
    """Custom permission model with codename-based access control."""
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["codename"]

    def __str__(self):
        return self.codename


class Role(models.Model):
    """Role grouping permissions together."""
    name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name="roles")

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    """Custom user manager using username as the unique identifier."""

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Le nom d'utilisateur est obligatoire")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser):
    """Custom user model with username authentication and role-based permissions."""
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, null=True, related_name="users")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    @property
    def permissions(self):
        """Return list of permission codenames via the user's role."""
        if self.role:
            return list(self.role.permissions.values_list("codename", flat=True))
        return []

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
