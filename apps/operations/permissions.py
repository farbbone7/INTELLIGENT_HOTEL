from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.core.permissions import get_object_hotel_id


class OperationsHotelAccess(BasePermission):
    message = "No tienes acceso a los registros operativos de este hotel."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or user.hotel_id is not None)
        )

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser:
            return True

        object_hotel_id = get_object_hotel_id(obj)

        return bool(
            user.hotel_id
            and object_hotel_id == user.hotel_id
        )


class IsOperationalTaskManager(OperationsHotelAccess):
    message = "No tienes permisos para administrar esta tarea."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        if request.method in SAFE_METHODS:
            return True

        user = request.user

        if user.is_superuser or user.role in ("GERENTE", "SUPERVISOR"):
            return True

        action = getattr(view, "action", None)

        if user.role == "COORDINADOR_EVENTOS":
            return action in ("create", "update", "partial_update")

        if user.role == "PERSONAL_OPERATIVO":
            return action in ("update", "partial_update")

        return False

    def has_object_permission(self, request, view, obj):
        if not super().has_object_permission(request, view, obj):
            return False

        user = request.user

        if user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return True

        action = getattr(view, "action", None)

        if user.role in ("GERENTE", "SUPERVISOR"):
            return True

        if user.role == "COORDINADOR_EVENTOS":
            return bool(
                action in ("update", "partial_update")
                and obj.event_id is not None
            )

        if user.role == "PERSONAL_OPERATIVO":
            return bool(
                action in ("update", "partial_update")
                and obj.assigned_employee
                and obj.assigned_employee.user_id == user.id
            )

        return False


class IsIncidentManager(OperationsHotelAccess):
    message = "No tienes permisos para administrar este incidente."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        if request.method in SAFE_METHODS:
            return True

        user = request.user

        if user.is_superuser or user.role in (
            "GERENTE",
            "SUPERVISOR",
        ):
            return True

        action = getattr(view, "action", None)

        return action == "create" and user.role in (
            "COORDINADOR_EVENTOS",
            "RECEPCION",
            "PERSONAL_OPERATIVO",
        )

    def has_object_permission(self, request, view, obj):
        if not super().has_object_permission(request, view, obj):
            return False

        user = request.user

        if user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return True

        return user.role in ("GERENTE", "SUPERVISOR")
