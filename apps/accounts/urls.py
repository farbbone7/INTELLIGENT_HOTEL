from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, CurrentUserView


urlpatterns = [
    path("login/", LoginView.as_view(), name="api-login"),
    path("refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),
    path("me/", CurrentUserView.as_view(), name="api-current-user"),
]
