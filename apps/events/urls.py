from rest_framework.routers import DefaultRouter

from apps.events.views import (
    EventSpaceViewSet,
    EventViewSet,
    EventStaffAssignmentViewSet,
)

router = DefaultRouter()

router.register("spaces", EventSpaceViewSet, basename="event-space")
router.register("events", EventViewSet, basename="event")
router.register("assignments", EventStaffAssignmentViewSet, basename="event-assignment")

urlpatterns = router.urls
