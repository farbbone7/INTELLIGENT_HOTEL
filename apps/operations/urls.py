from rest_framework.routers import DefaultRouter

from .views import OperationalTaskViewSet, IncidentViewSet


router = DefaultRouter()

router.register(
    "tasks",
    OperationalTaskViewSet,
    basename="operational-task",
)

router.register(
    "incidents",
    IncidentViewSet,
    basename="operational-incident",
)

urlpatterns = router.urls
