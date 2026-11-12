from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers

from apps.core.models import Hotel, OperationalArea
from .models import Employee, EmployeeShift, Position, Shift

User = get_user_model()


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = [
            "id",
            "name",
            "description",
            "is_active",
        ]
        read_only_fields = ["id"]


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = [
            "id",
            "name",
            "start_time",
            "end_time",
            "break_minutes",
            "description",
            "is_active",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        start_time = attrs.get(
            "start_time",
            getattr(self.instance, "start_time", None)
        )
        end_time = attrs.get(
            "end_time",
            getattr(self.instance, "end_time", None)
        )

        if start_time == end_time:
            raise serializers.ValidationError({
                "end_time": "La hora de finalización no puede ser igual al inicio."
            })

        return attrs


class EmployeeSerializer(serializers.ModelSerializer):
    hotel_id = serializers.PrimaryKeyRelatedField(
        source="hotel",
        queryset=Hotel.objects.all(),
        required=False
    )
    hotel_name = serializers.CharField(
        source="hotel.name",
        read_only=True
    )
    area_id = serializers.PrimaryKeyRelatedField(
        source="area",
        queryset=OperationalArea.objects.all()
    )
    area_name = serializers.CharField(
        source="area.name",
        read_only=True
    )
    position_id = serializers.PrimaryKeyRelatedField(
        source="position",
        queryset=Position.objects.all()
    )
    position_name = serializers.CharField(
        source="position.name",
        read_only=True
    )
    user_id = serializers.PrimaryKeyRelatedField(
        source="user",
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Employee
        fields = [
            "id",
            "hotel_id",
            "hotel_name",
            "user_id",
            "employee_code",
            "document_number",
            "first_name",
            "last_name",
            "email",
            "phone",
            "position_id",
            "position_name",
            "area_id",
            "area_name",
            "hire_date",
            "employment_status",
            "emergency_contact",
            "emergency_phone",
            "observations",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "hotel_name",
            "area_name",
            "position_name",
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

        hotel = attrs.get(
            "hotel",
            self.instance.hotel if self.instance else None
        )
        area = attrs.get(
            "area",
            self.instance.area if self.instance else None
        )
        position = attrs.get(
            "position",
            self.instance.position if self.instance else None
        )
        linked_user = attrs.get(
            "user",
            self.instance.user if self.instance else None
        )

        if not hotel:
            raise serializers.ValidationError({
                "hotel_id": "Debe seleccionar un hotel."
            })

        if area and area.hotel_id != hotel.id:
            raise serializers.ValidationError({
                "area_id": "El área seleccionada no pertenece al hotel indicado."
            })

        if position and not position.is_active:
            raise serializers.ValidationError({
                "position_id": "No se puede asignar un cargo inactivo."
            })

        if linked_user:
            if linked_user.is_superuser:
                raise serializers.ValidationError({
                    "user_id": "No se puede vincular un superusuario como empleado."
                })

            if linked_user.hotel_id != hotel.id:
                raise serializers.ValidationError({
                    "user_id": "El usuario debe pertenecer al mismo hotel del empleado."
                })

        return attrs


class EmployeeShiftSerializer(serializers.ModelSerializer):
    employee_id = serializers.PrimaryKeyRelatedField(
        source="employee",
        queryset=Employee.objects.select_related("hotel", "area", "position").all()
    )
    employee_name = serializers.SerializerMethodField()
    shift_id = serializers.PrimaryKeyRelatedField(
        source="shift",
        queryset=Shift.objects.all()
    )
    shift_name = serializers.CharField(
        source="shift.name",
        read_only=True
    )
    hotel_id = serializers.IntegerField(
        source="employee.hotel_id",
        read_only=True
    )
    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = EmployeeShift
        fields = [
            "id",
            "hotel_id",
            "employee_id",
            "employee_name",
            "shift_id",
            "shift_name",
            "work_date",
            "start_datetime",
            "end_datetime",
            "status",
            "observations",
            "created_by",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "hotel_id",
            "employee_name",
            "shift_name",
            "created_by",
            "created_at",
        ]

    def get_employee_name(self, obj) -> str:
        return f"{obj.employee.first_name} {obj.employee.last_name}"

    def validate(self, attrs):
        employee = attrs.get(
            "employee",
            self.instance.employee if self.instance else None
        )
        shift = attrs.get(
            "shift",
            self.instance.shift if self.instance else None
        )
        start = attrs.get(
            "start_datetime",
            self.instance.start_datetime if self.instance else None
        )
        end = attrs.get(
            "end_datetime",
            self.instance.end_datetime if self.instance else None
        )
        work_date = attrs.get(
            "work_date",
            self.instance.work_date if self.instance else None
        )
        status = attrs.get(
            "status",
            self.instance.status if self.instance else EmployeeShift.ShiftStatus.SCHEDULED
        )

        if employee and employee.employment_status != Employee.EmploymentStatus.ACTIVE:
            raise serializers.ValidationError({
                "employee_id": "Solo se pueden programar turnos a empleados activos."
            })

        if shift and not shift.is_active:
            raise serializers.ValidationError({
                "shift_id": "No se puede asignar un tipo de turno inactivo."
            })

        if start and end and end <= start:
            raise serializers.ValidationError({
                "end_datetime": "La finalización debe ser posterior al inicio."
            })

        if start and work_date and start.date() != work_date:
            raise serializers.ValidationError({
                "work_date": "La fecha de trabajo debe coincidir con la fecha de inicio del turno."
            })

        if employee and start and end and status in [
            EmployeeShift.ShiftStatus.SCHEDULED,
            EmployeeShift.ShiftStatus.CONFIRMED,
        ]:
            overlapping = EmployeeShift.objects.filter(
                employee=employee,
                status__in=[
                    EmployeeShift.ShiftStatus.SCHEDULED,
                    EmployeeShift.ShiftStatus.CONFIRMED,
                ],
                start_datetime__lt=end,
                end_datetime__gt=start,
            )

            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise serializers.ValidationError({
                    "start_datetime": "El empleado ya tiene un turno programado o confirmado en ese horario."
                })

        return attrs

