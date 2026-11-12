from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/auth/", include("apps.accounts.urls")),
    path("api/core/", include("apps.core.urls")),
    path("api/staff/", include("apps.staff.urls")),
    path("api/events/", include("apps.events.urls")),
    path("api/services/", include("apps.services.urls")),
    path("api/operations/", include("apps.operations.urls")),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
