from rest_framework import mixins, viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import OperationalTask, Incident
from .serializers import OperationalTaskSerializer, IncidentSerializer
from .permissions import IsOperationalTaskManager, IsIncidentManager


class OperationalTaskViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = OperationalTaskSerializer
    permission_classes = [IsOperationalTaskManager]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "area",
        "event",
        "service_request",
        "assigned_employee",
        "priority",
        "status",
    ]

    search_fields = [
        "code",
        "title",
        "description",
        "assigned_employee__first_name",
        "assigned_employee__last_name",
    ]

    ordering_fields = [
        "created_at",
        "due_at",
        "priority",
        "status",
        "completed_at",
    ]

    ordering = ["due_at", "-priority"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return OperationalTask.objects.none()

        user = self.request.user

        queryset = OperationalTask.objects.select_related(
            "hotel",
            "area",
            "event",
            "service_request",
            "assigned_employee",
            "created_by",
        )

        if user.is_superuser:
            return queryset.all()

        if not user.hotel_id:
            return OperationalTask.objects.none()

        queryset = queryset.filter(hotel_id=user.hotel_id)

        if user.role == "PERSONAL_OPERATIVO":
            return queryset.filter(
                assigned_employee__user_id=user.id
            )

        if user.role == "COORDINADOR_EVENTOS":
            return queryset.filter(event__isnull=False)

        return queryset


class IncidentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = IncidentSerializer
    permission_classes = [IsIncidentManager]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "area",
        "event",
        "service_request",
        "employee",
        "severity",
        "status",
    ]

    search_fields = [
        "code",
        "title",
        "description",
        "employee__first_name",
        "employee__last_name",
    ]

    ordering_fields = [
        "reported_at",
        "severity",
        "status",
        "resolved_at",
    ]

    ordering = ["-reported_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Incident.objects.none()

        user = self.request.user

        queryset = Incident.objects.select_related(
            "hotel",
            "area",
            "service_request",
            "event",
            "employee",
            "reported_by",
        )

        if user.is_superuser:
            return queryset.all()

        if not user.hotel_id:
            return Incident.objects.none()

        queryset = queryset.filter(hotel_id=user.hotel_id)

        if user.role == "PERSONAL_OPERATIVO":
            return queryset.filter(
                employee__user_id=user.id
            )

        if user.role == "COORDINADOR_EVENTOS":
            return queryset.filter(event__isnull=False)

        return queryset
