from rest_framework.routers import DefaultRouter

from .views import (
    EmployeeShiftViewSet,
    EmployeeViewSet,
    PositionViewSet,
    ShiftViewSet,
)

router = DefaultRouter()
router.register("positions", PositionViewSet, basename="position")
router.register("employees", EmployeeViewSet, basename="employee")
router.register("shifts", ShiftViewSet, basename="shift")
router.register("employee-shifts", EmployeeShiftViewSet, basename="employee-shift")

urlpatterns = router.urls
