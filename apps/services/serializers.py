import uuid

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.core.models import Hotel, OperationalArea
from apps.staff.models import Employee
from .models import ServiceType, ServiceRequest, RequestHistory


class ServiceTypeSerializer(serializers.ModelSerializer):
    hotel = serializers.PrimaryKeyRelatedField(
        queryset=Hotel.objects.all()
    )
    area = serializers.PrimaryKeyRelatedField(
        queryset=OperationalArea.objects.all()
    )

    class Meta:
        model = ServiceType
        fields = [
            "id",
            "hotel",
            "area",
            "code",
            "name",
            "category",
            "description",
            "target_minutes",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            if not request.user.is_superuser:
                hotel_id = request.user.hotel_id
                self.fields["hotel"].queryset = Hotel.objects.filter(
                    id=hotel_id
                )
                self.fields["area"].queryset = OperationalArea.objects.filter(
                    hotel_id=hotel_id
                )

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None

        if user and not user.is_superuser:
            validated_data["hotel"] = user.hotel

        return super().create(validated_data)

    def validate(self, attrs):
        hotel = attrs.get("hotel", getattr(self.instance, "hotel", None))
        area = attrs.get("area", getattr(self.instance, "area", None))

        if hotel and area and area.hotel_id != hotel.id:
            raise serializers.ValidationError(
                {"area": "El área debe pertenecer al mismo hotel del servicio."}
            )

        return attrs


class ServiceRequestSerializer(serializers.ModelSerializer):
    hotel = serializers.PrimaryKeyRelatedField(
        queryset=Hotel.objects.all()
    )
    service_type = serializers.PrimaryKeyRelatedField(
        queryset=ServiceType.objects.all()
    )
    assigned_area = serializers.PrimaryKeyRelatedField(
        queryset=OperationalArea.objects.all(),
        required=True,
        allow_null=False,
    )
    assigned_employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ServiceRequest
        fields = [
            "id",
            "hotel",
            "service_type",
            "request_code",
            "guest_name",
            "room_number",
            "contact_phone",
            "description",
            "priority",
            "status",
            "channel",
            "assigned_area",
            "assigned_employee",
            "requested_at",
            "response_deadline",
            "first_response_at",
            "resolved_at",
            "closed_at",
            "resolution_notes",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "request_code",
            "requested_at",
            "first_response_at",
            "resolved_at",
            "closed_at",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            user = request.user

            if not user.is_superuser:
                hotel_id = user.hotel_id

                self.fields["hotel"].queryset = Hotel.objects.filter(
                    id=hotel_id
                )
                self.fields["hotel"].required = False
                self.fields["hotel"].read_only = True

                self.fields["service_type"].queryset = (
                    ServiceType.objects.filter(
                        hotel_id=hotel_id,
                        is_active=True,
                    )
                )
                self.fields["assigned_area"].queryset = (
                    OperationalArea.objects.filter(
                        hotel_id=hotel_id,
                        is_active=True,
                    )
                )
                self.fields["assigned_employee"].queryset = (
                    Employee.objects.filter(
                        hotel_id=hotel_id,
                        employment_status="ACTIVE",
                    )
                )

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user if request else None

        hotel = attrs.get(
            "hotel",
            getattr(self.instance, "hotel", None),
        )

        if user and not user.is_superuser:
            hotel = Hotel.objects.filter(id=user.hotel_id).first()

        if hotel is None:
            raise serializers.ValidationError(
                {"hotel": "Debes seleccionar un hotel válido."}
            )

        service_type = attrs.get(
            "service_type",
            getattr(self.instance, "service_type", None),
        )
        assigned_area = attrs.get(
            "assigned_area",
            getattr(self.instance, "assigned_area", None),
        )
        assigned_employee = attrs.get(
            "assigned_employee",
            getattr(self.instance, "assigned_employee", None),
        )

        if service_type and service_type.hotel_id != hotel.id:
            raise serializers.ValidationError({
                "service_type": "El tipo de servicio no pertenece al hotel."
            })

        if assigned_area and assigned_area.hotel_id != hotel.id:
            raise serializers.ValidationError({
                "assigned_area": "El área asignada no pertenece al hotel."
            })

        if assigned_employee:
            if assigned_employee.hotel_id != hotel.id:
                raise serializers.ValidationError({
                    "assigned_employee": "El empleado pertenece a otro hotel."
                })

            if assigned_employee.employment_status != "ACTIVE":
                raise serializers.ValidationError({
                    "assigned_employee": "El empleado no está activo."
                })

            if assigned_area and assigned_employee.area_id:
                if assigned_employee.area_id != assigned_area.id:
                    raise serializers.ValidationError({
                        "assigned_employee": (
                            "El empleado no pertenece al área asignada."
                        )
                    })

        if user and not user.is_superuser:
            if user.role == "RECEPCION" and self.instance:
                raise serializers.ValidationError(
                    "Recepción puede crear solicitudes, pero no modificarlas."
                )

            if user.role == "PERSONAL_OPERATIVO":
                if not self.instance:
                    raise serializers.ValidationError(
                        "El personal operativo no puede crear solicitudes."
                    )

                if assigned_employee is None:
                    raise serializers.ValidationError({
                        "assigned_employee": "La solicitud debe tener un responsable."
                    })

                if assigned_employee.user_id != user.id:
                    raise serializers.ValidationError(
                        "Solo puedes gestionar solicitudes asignadas a tu usuario."
                    )

                allowed_fields = {"status", "resolution_notes"}
                submitted_fields = set(attrs.keys())

                if submitted_fields - allowed_fields:
                    raise serializers.ValidationError(
                        "Solo puedes actualizar el estado y las notas de resolución."
                    )

                new_status = attrs.get(
                    "status",
                    self.instance.status,
                )

                allowed_statuses = {
                    "IN_PROGRESS",
                    "ON_HOLD",
                    "RESOLVED",
                }

                if new_status not in allowed_statuses:
                    raise serializers.ValidationError({
                        "status": (
                            "Solo puedes pasar la solicitud a En proceso, "
                            "En espera o Resuelta."
                        )
                    })

        return attrs

    def _generate_request_code(self, hotel):
        while True:
            code = (
                f"SOL-{timezone.localdate():%Y%m%d}-"
                f"{uuid.uuid4().hex[:8].upper()}"
            )

            if not ServiceRequest.objects.filter(
                hotel=hotel,
                request_code=code,
            ).exists():
                return code

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None

        if user and not user.is_superuser:
            validated_data["hotel"] = user.hotel

        hotel = validated_data["hotel"]

        validated_data["request_code"] = self._generate_request_code(hotel)
        validated_data["status"] = "RECEIVED"

        if user and user.is_authenticated:
            validated_data["created_by"] = user
            validated_data["updated_by"] = user

        instance = super().create(validated_data)

        RequestHistory.objects.create(
            request=instance,
            previous_status="",
            new_status=instance.status,
            observations="Solicitud registrada.",
            changed_by=user if user and user.is_authenticated else None,
        )

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user if request else None

        previous_status = instance.status
        new_status = validated_data.get("status", previous_status)

        if user and user.is_authenticated:
            validated_data["updated_by"] = user

        if (
            new_status == "IN_PROGRESS"
            and not instance.first_response_at
        ):
            validated_data["first_response_at"] = timezone.now()

        if new_status == "RESOLVED":
            validated_data["resolved_at"] = timezone.now()

        if new_status == "CLOSED":
            validated_data["closed_at"] = timezone.now()

        updated_instance = super().update(instance, validated_data)

        if previous_status != updated_instance.status:
            observations = (
                validated_data.get("resolution_notes")
                or f"Estado actualizado a {updated_instance.status}."
            )

            RequestHistory.objects.create(
                request=updated_instance,
                previous_status=previous_status,
                new_status=updated_instance.status,
                observations=observations,
                changed_by=user if user and user.is_authenticated else None,
            )

        return updated_instance


class RequestHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestHistory
        fields = [
            "id",
            "request",
            "previous_status",
            "new_status",
            "observations",
            "changed_by",
            "changed_at",
        ]
        read_only_fields = fields
