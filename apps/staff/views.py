from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Employee, EmployeeShift, Position, Shift
from .permissions import (
    IsHotelEmployeeManager,
    IsHotelShiftManager,
    IsPlatformCatalogAdministrator,
)
from .serializers import (
    EmployeeSerializer,
    EmployeeShiftSerializer,
    PositionSerializer,
    ShiftSerializer,
)


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [IsPlatformCatalogAdministrator]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "is_active"]
    ordering = ["name"]


class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [IsPlatformCatalogAdministrator]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "start_time", "end_time", "is_active"]
    ordering = ["start_time"]


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.none()
    serializer_class = EmployeeSerializer
    permission_classes = [IsHotelEmployeeManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        "area_id",
        "position_id",
        "employment_status",
        "hotel_id",
    ]
    search_fields = [
        "employee_code",
        "document_number",
        "first_name",
        "last_name",
        "email",
        "position__name",
        "area__name",
    ]
    ordering_fields = [
        "first_name",
        "last_name",
        "hire_date",
        "employment_status",
        "created_at",
    ]
    ordering = ["last_name", "first_name"]

    def get_queryset(self):
        queryset = Employee.objects.select_related(
            "hotel", "area", "position", "user"
        )

        if getattr(self, "swagger_fake_view", False):
            return queryset.none()

        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()

        if user.is_superuser:
            return queryset

        if not user.hotel_id:
            return queryset.none()

        return queryset.filter(hotel_id=user.hotel_id)


class EmployeeShiftViewSet(viewsets.ModelViewSet):
    queryset = EmployeeShift.objects.none()
    serializer_class = EmployeeShiftSerializer
    permission_classes = [IsHotelShiftManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        "employee_id",
        "shift_id",
        "work_date",
        "status",
    ]
    search_fields = [
        "employee__employee_code",
        "employee__document_number",
        "employee__first_name",
        "employee__last_name",
        "shift__name",
    ]
    ordering_fields = [
        "work_date",
        "start_datetime",
        "end_datetime",
        "status",
        "created_at",
    ]
    ordering = ["-work_date", "start_datetime"]

    def get_queryset(self):
        queryset = EmployeeShift.objects.select_related(
            "employee",
            "employee__hotel",
            "employee__area",
            "employee__position",
            "shift",
            "created_by",
        )

        if getattr(self, "swagger_fake_view", False):
            return queryset.none()

        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()

        if user.is_superuser:
            return queryset

        if not user.hotel_id:
            return queryset.none()

        return queryset.filter(employee__hotel_id=user.hotel_id)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
