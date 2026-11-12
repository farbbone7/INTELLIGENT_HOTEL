from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.core.permissions import get_object_hotel_id


class StaffHotelAccess(BasePermission):
    """
    Acceso de lectura para usuarios asociados a un hotel.
    El administrador de plataforma tiene acceso global.
    """

    message = "No tienes acceso al personal de este hotel."

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


class IsPlatformCatalogAdministrator(BasePermission):
    """
    Los cargos y tipos de turno son catálogos globales.
    Solamente el administrador de plataforma puede modificarlos.
    """

    message = "Solo el administrador de plataforma puede modificar este catálogo."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return bool(user.is_superuser or user.hotel_id is not None)

        return bool(user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsHotelEmployeeManager(StaffHotelAccess):
    """
    El gerente administra los empleados de su hotel.
    El supervisor y los demás roles solamente consultan.
    """

    message = "Se requieren permisos de gerente para administrar empleados."

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

        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user.is_superuser
            or request.user.role == "GERENTE"
        )


class IsHotelShiftManager(StaffHotelAccess):
    """
    El gerente y el supervisor pueden gestionar los turnos
    exclusivamente dentro de su hotel.
    """

    message = "Se requieren permisos de gerente o supervisor para gestionar turnos."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        user = request.user

        if request.method in SAFE_METHODS:
            return True

        return bool(
            user.is_superuser
            or user.role in ("GERENTE", "SUPERVISOR")
        )

    def has_object_permission(self, request, view, obj):
        if not super().has_object_permission(request, view, obj):
            return False

        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user.is_superuser
            or request.user.role in ("GERENTE", "SUPERVISOR")
        )
