from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.core.permissions import get_object_hotel_id


class EventsHotelAccess(BasePermission):
    message = "No tienes acceso a los eventos de este hotel."

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
            and object_hotel_id is not None
            and object_hotel_id == user.hotel_id
        )


class IsHotelEventManager(EventsHotelAccess):
    message = "Esta operación requiere permisos de gerente o coordinador de eventos."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        user = request.user

        if request.method in SAFE_METHODS:
            return True

        return bool(
            user.is_superuser
            or user.role in ("GERENTE", "COORDINADOR_EVENTOS")
        )

    def has_object_permission(self, request, view, obj):
        if not super().has_object_permission(request, view, obj):
            return False

        user = request.user

        if request.method in SAFE_METHODS:
            return True

        return bool(
            user.is_superuser
            or user.role in ("GERENTE", "COORDINADOR_EVENTOS")
        )


class IsHotelEventSpaceManager(EventsHotelAccess):
    message = "Solo el gerente del hotel puede administrar los espacios para eventos."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        user = request.user

        if request.method in SAFE_METHODS:
            return True

        return bool(user.is_superuser or user.role == "GERENTE")

    def has_object_permission(self, request, view, obj):
        if not super().has_object_permission(request, view, obj):
            return False

        user = request.user

        if request.method in SAFE_METHODS:
            return True

        return bool(user.is_superuser or user.role == "GERENTE")
