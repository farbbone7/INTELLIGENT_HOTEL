
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class HotelTokenObtainPairSerializer(TokenObtainPairSerializer):

    username_field = User.USERNAME_FIELD

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        if not user.is_active:
            raise serializers.ValidationError(
                "La cuenta se encuentra desactivada."
            )

        if not user.is_superuser:
            if not user.hotel_id:
                raise serializers.ValidationError(
                    "El usuario no tiene un hotel asignado."
                )

            if not user.hotel.is_active:
                raise serializers.ValidationError(
                    "El hotel asociado se encuentra inactivo."
                )

        refresh = self.get_token(user)

        refresh["role"] = user.role
        refresh["hotel_id"] = user.hotel_id

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        return data


class CurrentUserSerializer(serializers.ModelSerializer):

    hotel_id = serializers.IntegerField(
        source="hotel.id",
        read_only=True,
        allow_null=True
    )

    hotel_name = serializers.CharField(
        source="hotel.name",
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "hotel_id",
            "hotel_name",
            "is_active",
            "is_staff",
            "is_superuser",
        ]
        read_only_fields = fields
