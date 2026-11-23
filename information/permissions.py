from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.authtoken.models import Token


def admin_user_from_request(request):
    header = request.META.get("HTTP_AUTHORIZATION", "")
    if header.startswith("Bearer "):
        key = header[7:].strip()
    elif header.startswith("Token "):
        key = header[6:].strip()
    else:
        return None
    if not key:
        return None
    try:
        token = Token.objects.select_related("user").get(key=key)
    except Token.DoesNotExist:
        return None
    user = token.user
    if not user.is_active or getattr(user, "user_type", "") != "admin":
        return None
    return user


class IsAdmin(BasePermission):
    """Signed-in portfolio admins only."""

    def has_permission(self, request, view):
        return admin_user_from_request(request) is not None


class IsAdminOrReadOnly(BasePermission):
    """Public reads stay open. Creates, edits, and deletes require an admin token."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return admin_user_from_request(request) is not None
