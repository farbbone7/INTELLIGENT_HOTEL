from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from apps.events.models import Event, EventSpace, EventStaffAssignment
from apps.events.permissions import (
    IsHotelEventManager,
    IsHotelEventSpaceManager,
)
from apps.events.serializers import (
    EventSerializer,
    EventSpaceSerializer,
    EventStaffAssignmentSerializer,
)


class EventSpaceViewSet(viewsets.ModelViewSet):
    serializer_class = EventSpaceSerializer
    permission_classes = [IsHotelEventSpaceManager]
    queryset = EventSpace.objects.none()

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["is_active", "has_audio_visual"]
    search_fields = ["name", "location", "description"]
    ordering_fields = ["name", "capacity", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return EventSpace.objects.none()

        user = self.request.user

        if not user.is_authenticated:
            return EventSpace.objects.none()

        queryset = EventSpace.objects.select_related("hotel")

        if user.is_superuser:
            return queryset

        if not user.hotel_id:
            return EventSpace.objects.none()

        return queryset.filter(hotel_id=user.hotel_id)


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsHotelEventManager]
    queryset = Event.objects.none()

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["status", "event_type", "space_id"]
    search_fields = [
        "code",
        "title",
        "client_name",
        "client_email",
        "client_phone",
    ]
    ordering_fields = [
        "start_datetime",
        "end_datetime",
        "created_at",
        "expected_guests",
    ]
    ordering = ["start_datetime"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Event.objects.none()

        user = self.request.user

        if not user.is_authenticated:
            return Event.objects.none()

        queryset = Event.objects.select_related(
            "hotel",
            "space",
            "created_by",
        )

        if user.is_superuser:
            return queryset

        if not user.hotel_id:
            return Event.objects.none()

        return queryset.filter(hotel_id=user.hotel_id)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EventStaffAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = EventStaffAssignmentSerializer
    permission_classes = [IsHotelEventManager]
    queryset = EventStaffAssignment.objects.none()

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "status",
        "event_id",
        "employee_id",
        "assigned_role",
    ]
    search_fields = [
        "event__code",
        "event__title",
        "employee__first_name",
        "employee__last_name",
        "employee__employee_code",
        "assigned_role",
    ]
    ordering_fields = [
        "start_datetime",
        "end_datetime",
        "status",
        "created_at",
    ]
    ordering = ["start_datetime"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return EventStaffAssignment.objects.none()

        user = self.request.user

        if not user.is_authenticated:
            return EventStaffAssignment.objects.none()

        queryset = EventStaffAssignment.objects.select_related(
            "event",
            "event__hotel",
            "event__space",
            "employee",
            "employee__hotel",
            "employee__area",
            "employee__position",
            "assigned_by",
        )

        if user.is_superuser:
            return queryset

        if not user.hotel_id:
            return EventStaffAssignment.objects.none()

        return queryset.filter(event__hotel_id=user.hotel_id)

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)
