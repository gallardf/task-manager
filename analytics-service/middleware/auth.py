import jwt
from django.conf import settings
from django.http import JsonResponse


class JWTAuthMiddleware:
    """
    Decode JWT from Authorization header and inject user info into request.
    Exempts health check path.
    """

    EXEMPT_PATHS = ["/api/health/",
                    "/api/analytics/docs",
                    "/api/analytics/schema"]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if any(request.path.startswith(p) for p in self.EXEMPT_PATHS):
            return self.get_response(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JsonResponse({"detail": "Token manquant"}, status=401)

        parts = auth_header.split(" ")
        if len(parts) != 2:
            return JsonResponse({"detail": "Token invalide"}, status=401)
        token = parts[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return JsonResponse({"detail": "Token expiré"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"detail": "Token invalide"}, status=401)

        request.user_info = {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "role": payload.get("role"),
        }
        request.user_permissions = payload.get("permissions", [])

        return self.get_response(request)
