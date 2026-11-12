from rest_framework.routers import DefaultRouter

from .views import HotelViewSet, OperationalAreaViewSet

router = DefaultRouter()
router.register("hotels", HotelViewSet, basename="hotel")
router.register("areas", OperationalAreaViewSet, basename="operational-area")

urlpatterns = router.urls
