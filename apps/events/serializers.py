from rest_framework import serializers

from apps.core.models import Hotel
from apps.staff.models import Employee
from .models import Event, EventSpace, EventStaffAssignment


class EventSpaceSerializer(serializers.ModelSerializer):
    hotel_id = serializers.PrimaryKeyRelatedField(
        source="hotel",
        queryset=Hotel.objects.all(),
        required=False,
    )
    hotel_name = serializers.CharField(source="hotel.name", read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user and user.is_authenticated and not user.is_superuser:
            self.fields["hotel_id"].queryset = Hotel.objects.filter(
                pk=user.hotel_id
            )

    class Meta:
        model = EventSpace
        fields = [
            "id",
            "hotel_id",
            "hotel_name",
            "name",
            "location",
            "capacity",
            "description",
            "has_audio_visual",
            "is_active",
        ]
        read_only_fields = ["id", "hotel_name"]

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user if request else None

        if user and not user.is_superuser:
            if not user.hotel_id:
                raise serializers.ValidationError(
                    "El usuario no tiene un hotel asignado."
                )
            attrs["hotel"] = user.hotel

        hotel = attrs.get("hotel", self.instance.hotel if self.instance else None)
        capacity = attrs.get(
            "capacity",
            self.instance.capacity if self.instance else None,
        )

        if not hotel:
            raise serializers.ValidationError({
                "hotel_id": "Debe seleccionar un hotel."
            })

        if capacity is not None and capacity <= 0:
            raise serializers.ValidationError({
                "capacity": "La capacidad debe ser mayor que cero."
            })

        return attrs


class EventSerializer(serializers.ModelSerializer):
    hotel_id = serializers.PrimaryKeyRelatedField(
        source="hotel",
        queryset=Hotel.objects.all(),
        required=False,
    )
    hotel_name = serializers.CharField(source="hotel.name", read_only=True)

    space_id = serializers.PrimaryKeyRelatedField(
        source="space",
        queryset=EventSpace.objects.all(),
    )
    space_name = serializers.CharField(source="space.name", read_only=True)

    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user and user.is_authenticated and not user.is_superuser:
            self.fields["hotel_id"].queryset = Hotel.objects.filter(
                pk=user.hotel_id
            )
            self.fields["space_id"].queryset = EventSpace.objects.filter(
                hotel_id=user.hotel_id
            )

    class Meta:
        model = Event
        fields = [
            "id",
            "hotel_id",
            "hotel_name",
            "space_id",
            "space_name",
            "code",
            "title",
            "event_type",
            "client_name",
            "client_email",
            "client_phone",
            "start_datetime",
            "end_datetime",
            "expected_guests",
            "status",
            "special_requirements",
            "setup_notes",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "hotel_name",
            "space_name",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user if request else None

        if user and not user.is_superuser:
            if not user.hotel_id:
                raise serializers.ValidationError(
                    "El usuario no tiene un hotel asignado."
                )
            attrs["hotel"] = user.hotel

        hotel = attrs.get("hotel", self.instance.hotel if self.instance else None)
        space = attrs.get("space", self.instance.space if self.instance else None)
        start = attrs.get(
            "start_datetime",
            self.instance.start_datetime if self.instance else None,
        )
        end = attrs.get(
            "end_datetime",
            self.instance.end_datetime if self.instance else None,
        )
        guests = attrs.get(
            "expected_guests",
            self.instance.expected_guests if self.instance else None,
        )
        status = attrs.get(
            "status",
            self.instance.status if self.instance else Event.EventStatus.REQUESTED,
        )

        if not hotel:
            raise serializers.ValidationError({
                "hotel_id": "Debe seleccionar un hotel."
            })

        if start and end and end <= start:
            raise serializers.ValidationError({
                "end_datetime": "La finalización debe ser posterior al inicio."
            })

        if space:
            if space.hotel_id != hotel.id:
                raise serializers.ValidationError({
                    "space_id": "El espacio no pertenece al hotel seleccionado."
                })

            if not space.is_active:
                raise serializers.ValidationError({
                    "space_id": "No se puede reservar un espacio inactivo."
                })

            if guests is not None and guests > space.capacity:
                raise serializers.ValidationError({
                    "expected_guests": "La cantidad de invitados supera la capacidad del espacio."
                })

        if space and start and end and status != Event.EventStatus.CANCELLED:
            overlapping = Event.objects.filter(
                space=space,
                status__in=[
                    Event.EventStatus.REQUESTED,
                    Event.EventStatus.CONFIRMED,
                    Event.EventStatus.PLANNING,
                    Event.EventStatus.IN_PROGRESS,
                ],
                start_datetime__lt=end,
                end_datetime__gt=start,
            )

            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise serializers.ValidationError({
                    "space_id": "El espacio ya tiene otro evento reservado en ese horario."
                })

        return attrs


class EventStaffAssignmentSerializer(serializers.ModelSerializer):
    event_id = serializers.PrimaryKeyRelatedField(
        source="event",
        queryset=Event.objects.select_related("hotel", "space").all(),
    )
    event_code = serializers.CharField(source="event.code", read_only=True)
    event_title = serializers.CharField(source="event.title", read_only=True)

    employee_id = serializers.PrimaryKeyRelatedField(
        source="employee",
        queryset=Employee.objects.select_related("hotel", "area", "position").all(),
    )
    employee_name = serializers.SerializerMethodField()
    employee_code = serializers.CharField(
        source="employee.employee_code",
        read_only=True,
    )

    assigned_by = serializers.PrimaryKeyRelatedField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user and user.is_authenticated and not user.is_superuser:
            self.fields["event_id"].queryset = Event.objects.filter(
                hotel_id=user.hotel_id
            )
            self.fields["employee_id"].queryset = Employee.objects.filter(
                hotel_id=user.hotel_id
            )

    class Meta:
        model = EventStaffAssignment
        fields = [
            "id",
            "event_id",
            "event_code",
            "event_title",
            "employee_id",
            "employee_name",
            "employee_code",
            "assigned_role",
            "start_datetime",
            "end_datetime",
            "status",
            "observations",
            "assigned_by",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "event_code",
            "event_title",
            "employee_name",
            "employee_code",
            "assigned_by",
            "created_at",
        ]

    def get_employee_name(self, obj) -> str:
        return f"{obj.employee.first_name} {obj.employee.last_name}"

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user if request else None

        event = attrs.get(
            "event",
            self.instance.event if self.instance else None,
        )
        employee = attrs.get(
            "employee",
            self.instance.employee if self.instance else None,
        )
        start = attrs.get(
            "start_datetime",
            self.instance.start_datetime if self.instance else None,
        )
        end = attrs.get(
            "end_datetime",
            self.instance.end_datetime if self.instance else None,
        )
        status = attrs.get(
            "status",
            self.instance.status if self.instance else EventStaffAssignment.AssignmentStatus.ASSIGNED,
        )

        if event and employee:
            if event.hotel_id != employee.hotel_id:
                raise serializers.ValidationError({
                    "employee_id": "El empleado debe pertenecer al hotel que organiza el evento."
                })

            if (
                user
                and not user.is_superuser
                and employee.hotel_id != user.hotel_id
            ):
                raise serializers.ValidationError({
                    "employee_id": "No puedes asignar personal de otro hotel."
                })

            if employee.employment_status != Employee.EmploymentStatus.ACTIVE:
                raise serializers.ValidationError({
                    "employee_id": "Solo se puede asignar personal con estado laboral activo."
                })

            if event.status == Event.EventStatus.CANCELLED:
                raise serializers.ValidationError({
                    "event_id": "No se puede asignar personal a un evento cancelado."
                })

        if start and end and end <= start:
            raise serializers.ValidationError({
                "end_datetime": "La finalización debe ser posterior al inicio."
            })

        if event and start and end:
            if start < event.start_datetime or end > event.end_datetime:
                raise serializers.ValidationError({
                    "start_datetime": "El horario de asignación debe estar dentro del horario del evento."
                })

        if (
            employee
            and start
            and end
            and status != EventStaffAssignment.AssignmentStatus.CANCELLED
        ):
            overlapping = EventStaffAssignment.objects.filter(
                employee=employee,
                status__in=[
                    EventStaffAssignment.AssignmentStatus.ASSIGNED,
                    EventStaffAssignment.AssignmentStatus.CONFIRMED,
                    EventStaffAssignment.AssignmentStatus.IN_PROGRESS,
                ],
                start_datetime__lt=end,
                end_datetime__gt=start,
            )

            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise serializers.ValidationError({
                    "start_datetime": "El empleado ya tiene otra asignación en ese horario."
                })

        return attrs
