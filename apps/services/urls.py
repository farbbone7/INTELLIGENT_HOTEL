from rest_framework.routers import DefaultRouter

from .views import (
    ServiceTypeViewSet,
    ServiceRequestViewSet,
    RequestHistoryViewSet,
)

router = DefaultRouter()

router.register(
    "types",
    ServiceTypeViewSet,
    basename="service-type",
)

router.register(
    "requests",
    ServiceRequestViewSet,
    basename="service-request",
)

router.register(
    "history",
    RequestHistoryViewSet,
    basename="request-history",
)

urlpatterns = router.urls
