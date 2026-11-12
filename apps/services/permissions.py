from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.core.permissions import get_object_hotel_id


class ServicesHotelAccess(BasePermission):
    message = "No tienes acceso a los registros de este hotel."

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

        if object_hotel_id is None and hasattr(obj, "request"):
            object_hotel_id = obj.request.hotel_id

        return bool(
            user.hotel_id
            and object_hotel_id == user.hotel_id
        )


class IsServiceTypeManager(ServicesHotelAccess):
    message = "Solo el gerente del hotel puede administrar los tipos de servicio."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        if request.method in SAFE_METHODS:
            return True

        user = request.user
        return bool(user.is_superuser or user.role == "GERENTE")

    def has_object_permission(self, request, view, obj):
        if not super().has_object_permission(request, view, obj):
            return False

        if request.method in SAFE_METHODS:
            return True

        user = request.user
        return bool(user.is_superuser or user.role == "GERENTE")


class IsServiceRequestManager(ServicesHotelAccess):
    message = "No tienes permisos para realizar esta operación sobre la solicitud."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        if request.method in SAFE_METHODS:
            return True

        user = request.user

        if user.is_superuser or user.role in ("GERENTE", "SUPERVISOR"):
            return True

        action = getattr(view, "action", None)

        if action == "create":
            return user.role == "RECEPCION"

        if action in ("partial_update", "update"):
            return user.role == "PERSONAL_OPERATIVO"

        return False

    def has_object_permission(self, request, view, obj):
        if not super().has_object_permission(request, view, obj):
            return False

        user = request.user

        if user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return True

        if user.role in ("GERENTE", "SUPERVISOR"):
            return True

        action = getattr(view, "action", None)

        if user.role == "PERSONAL_OPERATIVO":
            return bool(
                action in ("partial_update", "update")
                and obj.assigned_employee
                and obj.assigned_employee.user_id == user.id
            )

        return False


class IsRequestHistoryReadOnly(ServicesHotelAccess):
    message = "El historial de solicitudes es de solo lectura."

    def has_permission(self, request, view):
        return bool(
            super().has_permission(request, view)
            and request.method in SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        if request.method not in SAFE_METHODS:
            return False

        if not super().has_object_permission(request, view, obj):
            return False

        user = request.user

        if user.is_superuser:
            return True

        service_request = obj.request

        if user.role == "PERSONAL_OPERATIVO":
            return bool(
                service_request.assigned_employee
                and service_request.assigned_employee.user_id == user.id
            )

        if user.role == "COORDINADOR_EVENTOS":
            return bool(
                service_request.assigned_area
                and service_request.assigned_area.area_type == "EVENTS"
            )

        return True
