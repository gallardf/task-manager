import os

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, Role, Permission

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")


def validate_reserved_username(self, value):
    """Reject the protected admin username."""
    if value.lower() == ADMIN_USERNAME.lower():
        raise serializers.ValidationError(f"Le nom d'utilisateur '{ADMIN_USERNAME}' est réservé.")
    return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extend JWT payload with user role and permissions."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["role"] = user.role.name if user.role else None
        token["permissions"] = user.permissions
        return token


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "codename", "description"]


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ["id", "name", "permissions"]


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.name", read_only=True)
    permissions = serializers.ListField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "role", "role_name", "permissions",
            "is_active", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for admin user creation."""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "first_name", "last_name", "role"]
        read_only_fields = ["id"]

    validate_username = validate_reserved_username

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin user updates (role changes, etc.)."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "is_active"]
        read_only_fields = ["id", "username"]

    validate_username = validate_reserved_username

class UserSelfUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]
        read_only_fields = ["id"]
