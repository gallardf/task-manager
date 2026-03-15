from rest_framework import generics, serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import User, Role
from .permissions import IsAdmin
from .serializers import (
    ADMIN_USERNAME,
    CustomTokenObtainPairSerializer,
    RoleSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserSelfUpdateSerializer,
)


@extend_schema(tags=["Auth"])
class CustomTokenObtainPairView(TokenObtainPairView):
    """Authentification par username/password. Retourne un access token (15 min) et un refresh token (7 jours)."""
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(tags=["Users"])
class MeView(generics.RetrieveUpdateAPIView):
    """Profil de l'utilisateur connecté. GET pour consulter, PATCH pour modifier (email, prénom, nom)."""
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserSelfUpdateSerializer
        return UserSerializer


@extend_schema_view(
    list=extend_schema(summary="Lister les utilisateurs", tags=["Users"]),
    create=extend_schema(summary="Créer un utilisateur", tags=["Users"]),
    retrieve=extend_schema(summary="Détail d'un utilisateur", tags=["Users"]),
    update=extend_schema(summary="Modifier un utilisateur", tags=["Users"]),
    partial_update=extend_schema(summary="Modifier partiellement un utilisateur", tags=["Users"]),
    destroy=extend_schema(summary="Supprimer un utilisateur", tags=["Users"]),
)
class UserViewSet(viewsets.ModelViewSet):
    """CRUD des utilisateurs. Création, modification et suppression réservées à l'admin."""
    queryset = User.objects.select_related("role").all()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ("update", "partial_update"):
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdmin()]
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        user = self.get_object()
        if user.username == ADMIN_USERNAME:
            if "role" in serializer.validated_data and serializer.validated_data["role"] != user.role:
                raise serializers.ValidationError({"role": "Le rôle de l'administrateur principal ne peut pas être modifié."})
            if "is_active" in serializer.validated_data and not serializer.validated_data["is_active"]:
                raise serializers.ValidationError({"is_active": "L'administrateur principal ne peut pas être désactivé."})
        serializer.save()

    def perform_destroy(self, instance):
        if instance.username == "admin":
            raise serializers.ValidationError({"detail": "L'administrateur principal ne peut pas être supprimé."})
        instance.delete()

    @extend_schema(
        summary="Permissions d'un utilisateur",
        tags=["Users"],
        responses={200: {"type": "object", "properties": {"permissions": {"type": "array", "items": {"type": "string"}}}}},
    )
    @action(detail=True, methods=["get"])
    def permissions(self, request, pk=None):
        user = self.get_object()
        return Response({"permissions": user.permissions})


@extend_schema(tags=["Roles"])
class RoleListView(generics.ListAPIView):
    """Liste des rôles disponibles avec leurs permissions."""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
