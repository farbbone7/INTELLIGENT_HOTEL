import uuid

from django.utils import timezone
from rest_framework import serializers

from apps.core.models import Hotel, OperationalArea
from apps.events.models import Event
from apps.services.models import ServiceRequest
from apps.staff.models import Employee

from .models import OperationalTask, Incident


class OperationsRelatedQuerysetsMixin:

    def get_user(self):
        request = self.context.get("request")
        return getattr(request, "user", None)

    def get_hotel_id(self):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user is None or not getattr(user, "is_authenticated", False):
            return None

        if getattr(user, "is_superuser", False):
            return None

        return getattr(user, "hotel_id", None)

    def filter_hotel_queryset(self, queryset):
        hotel_id = self.get_hotel_id()

        if hotel_id is None:
            return queryset

        return queryset.filter(hotel_id=hotel_id)

    def get_fields(self):
        fields = super().get_fields()
        hotel_id = self.get_hotel_id()

        if hotel_id is not None:
            for field_name in (
                "hotel",
                "area",
                "event",
                "service_request",
                "assigned_employee",
                "employee",
            ):
                field = fields.get(field_name)

                if field is not None and hasattr(field, "queryset"):
                    if field_name == "hotel":
                        field.queryset = field.queryset.filter(id=hotel_id)
                    else:
                        field.queryset = self.filter_hotel_queryset(
                            field.queryset
                        )

        return fields


class OperationalTaskSerializer(
    OperationsRelatedQuerysetsMixin,
    serializers.ModelSerializer,
):

    hotel = serializers.PrimaryKeyRelatedField(
        queryset=Hotel.objects.all(),
        required=False,
    )

    area = serializers.PrimaryKeyRelatedField(
        queryset=OperationalArea.objects.all(),
    )

    event = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(),
        required=False,
        allow_null=True,
    )

    service_request = serializers.PrimaryKeyRelatedField(
        queryset=ServiceRequest.objects.all(),
        required=False,
        allow_null=True,
    )

    assigned_employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        required=False,
        allow_null=True,
    )

    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = OperationalTask
        fields = [
            "id",
            "hotel",
            "area",
            "event",
            "service_request",
            "code",
            "title",
            "description",
            "priority",
            "status",
            "assigned_employee",
            "due_at",
            "started_at",
            "completed_at",
            "completion_notes",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "started_at",
            "completed_at",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user = self.get_user()

        if not getattr(user, "is_superuser", False):
            self.fields["hotel"].read_only = True

        if getattr(user, "role", None) == "PERSONAL_OPERATIVO":
            for field_name in (
                "hotel",
                "area",
                "event",
                "service_request",
                "assigned_employee",
                "title",
                "description",
                "priority",
                "due_at",
            ):
                self.fields[field_name].read_only = True

    def validate(self, attrs):
        user = self.get_user()
        instance = self.instance

        hotel = attrs.get(
            "hotel",
            instance.hotel if instance else (
                None if getattr(user, "is_superuser", False) else user.hotel
            ),
        )

        area = attrs.get(
            "area",
            instance.area if instance else None,
        )

        employee = attrs.get(
            "assigned_employee",
            instance.assigned_employee if instance else None,
        )

        event = attrs.get(
            "event",
            instance.event if instance else None,
        )

        service_request = attrs.get(
            "service_request",
            instance.service_request if instance else None,
        )

        if hotel is None:
            raise serializers.ValidationError(
                {"hotel": "Debes seleccionar un hotel."}
            )

        if not hotel.is_active:
            raise serializers.ValidationError(
                {"hotel": "El hotel está inactivo."}
            )

        if area and area.hotel_id != hotel.id:
            raise serializers.ValidationError(
                {"area": "El área no pertenece al hotel seleccionado."}
            )

        if employee:
            if employee.hotel_id != hotel.id:
                raise serializers.ValidationError(
                    {"assigned_employee": "El empleado pertenece a otro hotel."}
                )

            if employee.employment_status != "ACTIVE":
                raise serializers.ValidationError(
                    {"assigned_employee": "El empleado no está activo."}
                )

        if event and event.hotel_id != hotel.id:
            raise serializers.ValidationError(
                {"event": "El evento pertenece a otro hotel."}
            )

        if service_request and service_request.hotel_id != hotel.id:
            raise serializers.ValidationError(
                {"service_request": "La solicitud pertenece a otro hotel."}
            )

        if event and event.status == "CANCELLED":
            raise serializers.ValidationError(
                {"event": "No puedes asignar tareas a un evento cancelado."}
            )

        if getattr(user, "role", None) == "COORDINADOR_EVENTOS":
            if not event:
                raise serializers.ValidationError(
                    {"event": "Las tareas de eventos deben estar vinculadas a un evento."}
                )

        if getattr(user, "role", None) == "PERSONAL_OPERATIVO":
            allowed_fields = {"status", "completion_notes"}

            submitted_fields = set(self.initial_data.keys())

            forbidden = submitted_fields - allowed_fields

            if forbidden:
                raise serializers.ValidationError(
                    "Solo puedes actualizar el estado y las notas de tus tareas."
                )

            new_status = attrs.get("status")

            if new_status and new_status not in (
                "IN_PROGRESS",
                "ON_HOLD",
                "COMPLETED",
            ):
                raise serializers.ValidationError(
                    {"status": "No puedes establecer ese estado."}
                )

        return attrs

    def create(self, validated_data):
        user = self.get_user()

        if not getattr(user, "is_superuser", False):
            validated_data["hotel"] = user.hotel

        validated_data["code"] = (
            f"TAR-{timezone.localdate():%Y%m%d}-"
            f"{uuid.uuid4().hex[:8].upper()}"
        )

        validated_data["created_by"] = user

        return super().create(validated_data)

    def update(self, instance, validated_data):
        new_status = validated_data.get("status")

        if new_status == "IN_PROGRESS" and not instance.started_at:
            validated_data["started_at"] = timezone.now()

        if new_status == "COMPLETED" and not instance.completed_at:
            validated_data["completed_at"] = timezone.now()

        return super().update(instance, validated_data)


class IncidentSerializer(
    OperationsRelatedQuerysetsMixin,
    serializers.ModelSerializer,
):

    hotel = serializers.PrimaryKeyRelatedField(
        queryset=Hotel.objects.all(),
        required=False,
    )

    area = serializers.PrimaryKeyRelatedField(
        queryset=OperationalArea.objects.all(),
    )

    event = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(),
        required=False,
        allow_null=True,
    )

    service_request = serializers.PrimaryKeyRelatedField(
        queryset=ServiceRequest.objects.all(),
        required=False,
        allow_null=True,
    )

    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        required=False,
        allow_null=True,
    )

    reported_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Incident
        fields = [
            "id",
            "hotel",
            "area",
            "service_request",
            "event",
            "employee",
            "code",
            "title",
            "description",
            "severity",
            "status",
            "reported_at",
            "investigation_notes",
            "corrective_actions",
            "resolved_at",
            "reported_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "reported_at",
            "resolved_at",
            "reported_by",
            "created_at",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user = self.get_user()
        role = getattr(user, "role", None)
        is_superuser = getattr(user, "is_superuser", False)

        if is_superuser or role in ("GERENTE", "SUPERVISOR"):
            return

        self.fields["hotel"].read_only = True

        if role == "RECEPCION":
            readonly_fields = (
                "employee",
                "status",
                "investigation_notes",
                "corrective_actions",
            )
        elif role == "PERSONAL_OPERATIVO":
            readonly_fields = (
                "area",
                "event",
                "service_request",
                "employee",
                "status",
                "investigation_notes",
                "corrective_actions",
            )
        elif role == "COORDINADOR_EVENTOS":
            readonly_fields = (
                "employee",
                "status",
                "investigation_notes",
                "corrective_actions",
            )
        else:
            readonly_fields = (
                "area",
                "event",
                "service_request",
                "employee",
                "title",
                "description",
                "severity",
                "investigation_notes",
                "corrective_actions",
                "status",
            )

        for field_name in readonly_fields:
            self.fields[field_name].read_only = True

    def validate(self, attrs):
        user = self.get_user()
        instance = self.instance
        role = getattr(user, "role", None)

        hotel = attrs.get(
            "hotel",
            instance.hotel if instance else (
                None if getattr(user, "is_superuser", False) else user.hotel
            ),
        )

        area = attrs.get(
            "area",
            instance.area if instance else None,
        )

        employee = attrs.get(
            "employee",
            instance.employee if instance else None,
        )

        event = attrs.get(
            "event",
            instance.event if instance else None,
        )

        service_request = attrs.get(
            "service_request",
            instance.service_request if instance else None,
        )

        if hotel is None:
            raise serializers.ValidationError(
                {"hotel": "Debes seleccionar un hotel."}
            )

        if role == "PERSONAL_OPERATIVO" and not instance:
            employee = Employee.objects.filter(
                hotel_id=user.hotel_id,
                user_id=user.id,
                employment_status="ACTIVE",
            ).select_related("area").first()

            if not employee:
                raise serializers.ValidationError(
                    "No existe un perfil de empleado activo asociado a tu usuario."
                )

            if not employee.area:
                raise serializers.ValidationError(
                    {"area": "Tu perfil de empleado no tiene un ?rea asignada."}
                )

            area = employee.area
            attrs["employee"] = employee
            attrs["area"] = area

        if area is None:
            raise serializers.ValidationError(
                {"area": "Debes seleccionar un ?rea para el incidente."}
            )

        if area.hotel_id != hotel.id:
            raise serializers.ValidationError(
                {"area": "El ?rea pertenece a otro hotel."}
            )

        if employee and employee.hotel_id != hotel.id:
            raise serializers.ValidationError(
                {"employee": "El empleado pertenece a otro hotel."}
            )

        if event and event.hotel_id != hotel.id:
            raise serializers.ValidationError(
                {"event": "El evento pertenece a otro hotel."}
            )

        if service_request and service_request.hotel_id != hotel.id:
            raise serializers.ValidationError(
                {"service_request": "La solicitud pertenece a otro hotel."}
            )

        return attrs

    def create(self, validated_data):
        user = self.get_user()

        if not getattr(user, "is_superuser", False):
            validated_data["hotel"] = user.hotel

        validated_data["code"] = (
            f"INC-{timezone.localdate():%Y%m%d}-"
            f"{uuid.uuid4().hex[:8].upper()}"
        )

        validated_data["reported_by"] = user

        return super().create(validated_data)

    def update(self, instance, validated_data):
        new_status = validated_data.get("status")

        if new_status == "RESOLVED" and not instance.resolved_at:
            validated_data["resolved_at"] = timezone.now()

        return super().update(instance, validated_data)
