from rest_framework import viewsets
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Hotel, OperationalArea
from .serializers import HotelSerializer, OperationalAreaSerializer
from .permissions import (
    IsPlatformAdministrator,
    IsHotelManager,
    HotelQuerySetMixin,
)


class CanAccessOwnHotel(BasePermission):
    message = "No tienes autorización para acceder a este hotel."

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

        return bool(
            user.hotel_id is not None
            and obj.pk == user.hotel_id
        )


class CanManageOwnHotel(BasePermission):
    message = "Solo el gerente del hotel o el administrador de plataforma pueden realizar esta operación."

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

        return bool(
            user.role == "GERENTE"
            and user.hotel_id is not None
            and obj.pk == user.hotel_id
        )


class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    search_fields = ["name", "commercial_name", "city", "tax_id"]
    ordering_fields = ["name", "city", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Hotel.objects.none()

        if user.is_superuser:
            return Hotel.objects.all()

        if not user.hotel_id:
            return Hotel.objects.none()

        return Hotel.objects.filter(pk=user.hotel_id)

    def get_permissions(self):
        if self.action in ["create", "destroy"]:
            permission_classes = [IsPlatformAdministrator]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsAuthenticated, CanManageOwnHotel]
        else:
            permission_classes = [IsAuthenticated, CanAccessOwnHotel]

        return [permission() for permission in permission_classes]


class OperationalAreaViewSet(
    HotelQuerySetMixin,
    viewsets.ModelViewSet
):
    queryset = OperationalArea.objects.select_related("hotel").all()
    serializer_class = OperationalAreaSerializer
    hotel_filter = "hotel_id"

    search_fields = ["name", "code", "description"]
    ordering_fields = ["name", "code", "created_at"]
    ordering = ["name"]

    filterset_fields = ["area_type", "is_active"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsHotelManager]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        user = self.request.user

        if user.is_superuser:
            if not serializer.validated_data.get("hotel"):
                raise PermissionDenied(
                    "El administrador de plataforma debe seleccionar un hotel."
                )
            serializer.save()
            return

        if not user.hotel_id or user.role != "GERENTE":
            raise PermissionDenied(
                "No tienes permisos para crear áreas operativas."
            )

        serializer.save(hotel=user.hotel)
