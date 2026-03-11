from rest_framework import generics, serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, Role
from .permissions import IsAdmin
from .serializers import (
    CustomTokenObtainPairSerializer,
    RoleSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view with extended JWT payload."""
    serializer_class = CustomTokenObtainPairSerializer


class MeView(generics.RetrieveAPIView):
    """Return the currently authenticated user."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    """CRUD operations on users (admin-only except retrieve)."""
    queryset = User.objects.select_related("role").all()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ("update", "partial_update"):
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ("list", "create", "update", "partial_update", "destroy"):
            return [IsAdmin()]
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        user = self.get_object()
        if user.username == "admin":
            if "role" in serializer.validated_data and serializer.validated_data["role"] != user.role:
                raise serializers.ValidationError({"role": "Le rôle de l'administrateur principal ne peut pas être modifié."})
            if "is_active" in serializer.validated_data and not serializer.validated_data["is_active"]:
                raise serializers.ValidationError({"is_active": "L'administrateur principal ne peut pas être désactivé."})
        serializer.save()

    def perform_destroy(self, instance):
        if instance.username == "admin":
            raise serializers.ValidationError({"detail": "L'administrateur principal ne peut pas être supprimé."})
        instance.delete()

    @action(detail=True, methods=["get"])
    def permissions(self, request, pk=None):
        user = self.get_object()
        return Response({"permissions": user.permissions})


class RoleListView(generics.ListAPIView):
    """List all available roles."""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class ValidateTokenView(APIView):
    """Validate a JWT token and return user info (for service-to-service calls)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.name if user.role else None,
            "permissions": user.permissions,
        })
