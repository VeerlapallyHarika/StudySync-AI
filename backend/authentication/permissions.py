"""Request-level permission classes based on JWT principals."""
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Allow only principals issued for the admin role."""

    message = 'Admin privileges are required to access this resource.'

    def has_permission(self, request, view) -> bool:
        principal = getattr(request, 'principal', None)
        return principal is not None and principal.is_admin


class IsStudent(BasePermission):
    """Allow only principals issued for a registered student."""

    message = 'A student session is required to access this resource.'

    def has_permission(self, request, view) -> bool:
        principal = getattr(request, 'principal', None)
        return principal is not None and principal.is_student


class HasPrincipal(BasePermission):
    """Allow any authenticated principal (admin or student)."""

    message = 'Authentication is required to access this resource.'

    def has_permission(self, request, view) -> bool:
        return getattr(request, 'principal', None) is not None
