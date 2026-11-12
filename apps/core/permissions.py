from rest_framework.permissions import BasePermission


def get_object_hotel_id(obj):
    """
    Obtiene el hotel propietario de un objeto.
    Soporta modelos con hotel directo y algunos modelos relacionados.
    """
    if hasattr(obj, "hotel_id"):
        return obj.hotel_id

    related_fields = (
        "employee",
        "service_request",
        "event",
        "operational_area",
        "area",
    )

    for field in related_fields:
        related_obj = getattr(obj, field, None)

        if related_obj is not None and hasattr(related_obj, "hotel_id"):
            return related_obj.hotel_id

    return None


class IsPlatformAdministrator(BasePermission):
    """
    Acceso exclusivo al superusuario de la plataforma.
    """

    message = "No tienes permisos de administrador de plataforma."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsHotelMember(BasePermission):
    """
    Permite el acceso a usuarios asociados a un hotel.
    El superusuario puede consultar todos los hoteles.
    """

    message = "No tienes un hotel asignado o no tienes autorización."

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or user.hotel_id is not None
            )
        )

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser:
            return True

        object_hotel_id = get_object_hotel_id(obj)

        return bool(
            user.hotel_id is not None
            and object_hotel_id is not None
            and object_hotel_id == user.hotel_id
        )


class IsHotelManager(BasePermission):
    """
    Permite la administración completa del hotel al gerente
    y de todos los hoteles al superusuario de plataforma.
    """

    message = "Esta operación requiere permisos de gerente del hotel."

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or (
                    user.hotel_id is not None
                    and user.role == "GERENTE"
                )
            )
        )

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser:
            return True

        object_hotel_id = get_object_hotel_id(obj)

        return bool(
            user.role == "GERENTE"
            and user.hotel_id is not None
            and object_hotel_id is not None
            and object_hotel_id == user.hotel_id
        )


class HotelQuerySetMixin:
    """
    Limita automáticamente las consultas al hotel del usuario.

    Para modelos relacionados con el hotel mediante otra entidad,
    se puede configurar hotel_filter en cada vista.
    """

    hotel_filter = "hotel_id"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()

        if user.is_superuser:
            return queryset

        if not user.hotel_id:
            return queryset.none()

        return queryset.filter(
            **{self.hotel_filter: user.hotel_id}
        )
