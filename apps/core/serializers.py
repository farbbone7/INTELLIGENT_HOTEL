from rest_framework import serializers

from .models import Hotel, OperationalArea


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = [
            "id",
            "name",
            "commercial_name",
            "category",
            "tax_id",
            "email",
            "phone",
            "address",
            "city",
            "country",
            "timezone",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OperationalAreaSerializer(serializers.ModelSerializer):
    hotel_id = serializers.PrimaryKeyRelatedField(
        source="hotel",
        queryset=Hotel.objects.all(),
        required=False
    )

    hotel_name = serializers.CharField(
        source="hotel.name",
        read_only=True
    )

    class Meta:
        model = OperationalArea
        fields = [
            "id",
            "hotel_id",
            "hotel_name",
            "code",
            "name",
            "area_type",
            "description",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "hotel_name", "created_at"]

    def validate(self, attrs):
        request = self.context.get("request")

        if request and not request.user.is_superuser:
            if not request.user.hotel_id:
                raise serializers.ValidationError(
                    "El usuario no tiene un hotel asignado."
                )

            # Los usuarios de hotel solo pueden operar sobre su propio hotel.
            # Se ignora cualquier hotel_id diferente enviado por el cliente.
            attrs["hotel"] = request.user.hotel

        hotel = attrs.get(
            "hotel",
            getattr(self.instance, "hotel", None)
        )

        code = attrs.get(
            "code",
            getattr(self.instance, "code", None)
        )

        if hotel and code:
            queryset = OperationalArea.objects.filter(
                hotel=hotel,
                code=code
            )

            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError({
                    "code": "Ya existe un área con este código en el hotel."
                })

        return attrs
