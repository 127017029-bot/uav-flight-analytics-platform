"""
Custom DRF permissions for the UAV Digital Twin Platform.

Provides role-based and ownership-based access control for API endpoints.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission that grants write access only to the object owner.

    Assumes the model instance has an ``owner`` attribute. Read-only methods
    (GET, HEAD, OPTIONS) are allowed for any authenticated user.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request.
        if request.method in SAFE_METHODS:
            return True

        # Write permissions require ownership.
        owner = getattr(obj, "owner", None) or getattr(obj, "user", None)
        return owner == request.user


class IsPilot(BasePermission):
    """
    Allows access only to users with the 'pilot' role.

    The user model must expose a ``role`` field or an ``is_pilot`` property.
    """

    message = "Only pilots are authorised to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Support both a dedicated role field and a convenience property.
        if hasattr(request.user, "is_pilot"):
            return request.user.is_pilot
        return getattr(request.user, "role", None) == "pilot"


class IsFleetManager(BasePermission):
    """
    Allows access only to users with the 'fleet_manager' role.

    Fleet managers have elevated privileges for fleet-wide operations such
    as scheduling maintenance, viewing aggregate analytics, and managing
    drone assignments.
    """

    message = "Only fleet managers are authorised to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if hasattr(request.user, "is_fleet_manager"):
            return request.user.is_fleet_manager
        return getattr(request.user, "role", None) == "fleet_manager"


class IsAdminOrFleetManager(BasePermission):
    """
    Allows access to staff users **or** fleet managers.

    Useful for administrative endpoints that should also be accessible
    to senior operational roles.
    """

    message = "Admin or fleet manager privileges are required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        if hasattr(request.user, "is_fleet_manager"):
            return request.user.is_fleet_manager
        return getattr(request.user, "role", None) == "fleet_manager"
