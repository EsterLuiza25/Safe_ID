from django.conf import settings
from rest_framework.permissions import BasePermission


class HasAPIKey(BasePermission):
    message = "API key ausente ou invalida."

    def has_permission(self, request, view):
        expected_key = getattr(settings, "SAFEGUARD_API_KEY", "")
        provided_key = request.headers.get("X-API-Key")
        return bool(expected_key and provided_key == expected_key)
