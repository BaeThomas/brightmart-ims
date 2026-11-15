from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsInventoryUser(BasePermission):
    message = "An inventory Staff or Manager role is required."

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and user.role in ["STAFF", "MANAGER"]
        )


class IsManagerOrReadOnly(BasePermission):
    message = "Only Managers can change these records."

    def has_permission(self, request, view):
        user = request.user

        if not (
            user
            and user.is_authenticated
            and user.is_active
            and user.role in ["STAFF", "MANAGER"]
        ):
            return False

        if request.method in SAFE_METHODS:
            return True

        return user.role == "MANAGER"