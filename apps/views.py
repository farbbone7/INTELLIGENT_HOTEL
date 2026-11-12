
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    CurrentUserSerializer,
    HotelTokenObtainPairSerializer,
)


class LoginView(TokenObtainPairView):
    serializer_class = HotelTokenObtainPairSerializer


class CurrentUserView(RetrieveAPIView):
    serializer_class = CurrentUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
