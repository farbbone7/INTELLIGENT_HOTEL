from rest_framework import mixins, viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import ServiceType, ServiceRequest, RequestHistory
from .serializers import (
    ServiceTypeSerializer,
    ServiceRequestSerializer,
    RequestHistorySerializer,
)
from .permissions import (
    IsServiceTypeManager,
    IsServiceRequestManager,
    IsRequestHistoryReadOnly,
)


class ServiceTypeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ServiceTypeSerializer
    permission_classes = [IsServiceTypeManager]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = ["category", "area", "is_active"]
    search_fields = ["code", "name", "description"]
    ordering_fields = ["name", "target_minutes", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ServiceType.objects.none()

        user = self.request.user

        if user.is_superuser:
            return ServiceType.objects.select_related(
                "hotel", "area"
            ).all()

        if not user.hotel_id:
            return ServiceType.objects.none()

        return ServiceType.objects.select_related(
            "hotel", "area"
        ).filter(
            hotel_id=user.hotel_id
        )


class ServiceRequestViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ServiceRequestSerializer
    permission_classes = [IsServiceRequestManager]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "status",
        "priority",
        "channel",
        "assigned_area",
        "assigned_employee",
        "service_type",
    ]

    search_fields = [
        "request_code",
        "guest_name",
        "room_number",
        "description",
        "contact_phone",
    ]

    ordering_fields = [
        "requested_at",
        "response_deadline",
        "priority",
        "status",
        "created_at",
    ]

    ordering = ["-requested_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ServiceRequest.objects.none()

        user = self.request.user

        queryset = ServiceRequest.objects.select_related(
            "hotel",
            "service_type",
            "assigned_area",
            "assigned_employee",
            "created_by",
            "updated_by",
        )

        if user.is_superuser:
            return queryset.all()

        if not user.hotel_id:
            return ServiceRequest.objects.none()

        queryset = queryset.filter(hotel_id=user.hotel_id)

        if user.role == "PERSONAL_OPERATIVO":
            return queryset.filter(
                assigned_employee__user_id=user.id
            )

        if user.role == "COORDINADOR_EVENTOS":
            return queryset.filter(
                assigned_area__area_type="EVENTS"
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class RequestHistoryViewSet(
    viewsets.ReadOnlyModelViewSet,
):
    serializer_class = RequestHistorySerializer
    permission_classes = [IsRequestHistoryReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_fields = ["request", "new_status"]
    ordering_fields = ["changed_at"]
    ordering = ["-changed_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return RequestHistory.objects.none()

        user = self.request.user

        queryset = RequestHistory.objects.select_related(
            "request",
            "request__hotel",
            "request__assigned_employee",
            "changed_by",
        )

        if user.is_superuser:
            return queryset.all()

        if not user.hotel_id:
            return RequestHistory.objects.none()

        queryset = queryset.filter(
            request__hotel_id=user.hotel_id
        )

        if user.role == "PERSONAL_OPERATIVO":
            return queryset.filter(
                request__assigned_employee__user_id=user.id
            )

        if user.role == "COORDINADOR_EVENTOS":
            return queryset.filter(
                request__assigned_area__area_type="EVENTS"
            )

        return queryset
