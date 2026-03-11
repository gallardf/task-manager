from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

router = DefaultRouter()
router.register(r"users", views.UserViewSet)

urlpatterns = [
    path("auth/login/", views.CustomTokenObtainPairView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("users/me/", views.MeView.as_view(), name="me"),
    path("", include(router.urls)),
    path("roles/", views.RoleListView.as_view(), name="role-list"),
]
