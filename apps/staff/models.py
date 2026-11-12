from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.core.models import Hotel, OperationalArea


class Position(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Employee(models.Model):

    class EmploymentStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Activo"
        VACATION = "VACATION", "Vacaciones"
        LEAVE = "LEAVE", "Licencia"
        SUSPENDED = "SUSPENDED", "Suspendido"
        INACTIVE = "INACTIVE", "Retirado"

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.PROTECT,
        related_name="employees"
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_profile"
    )
    employee_code = models.CharField(max_length=30)
    document_number = models.CharField(max_length=30)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        related_name="employees"
    )
    area = models.ForeignKey(
        OperationalArea,
        on_delete=models.PROTECT,
        related_name="employees"
    )
    hire_date = models.DateField()
    employment_status = models.CharField(
        max_length=15,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE
    )
    emergency_contact = models.CharField(max_length=150, blank=True)
    emergency_phone = models.CharField(max_length=30, blank=True)
    observations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ["last_name", "first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["hotel", "employee_code"],
                name="unique_employee_code_per_hotel"
            ),
            models.UniqueConstraint(
                fields=["hotel", "document_number"],
                name="unique_document_per_hotel"
            ),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.employee_code}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.area_id and self.hotel_id:
            if self.area.hotel_id != self.hotel_id:
                raise ValidationError(
                    {"area": "El área debe pertenecer al mismo hotel del empleado."}
                )


class Shift(models.Model):
    name = models.CharField(max_length=80, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_minutes = models.PositiveSmallIntegerField(default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de turno"
        verbose_name_plural = "Tipos de turno"
        ordering = ["start_time"]

    def __str__(self):
        return self.name


class EmployeeShift(models.Model):

    class ShiftStatus(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Programado"
        CONFIRMED = "CONFIRMED", "Confirmado"
        COMPLETED = "COMPLETED", "Finalizado"
        CANCELLED = "CANCELLED", "Cancelado"

    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="scheduled_shifts"
    )
    shift = models.ForeignKey(
        Shift,
        on_delete=models.PROTECT,
        related_name="employee_schedules"
    )
    work_date = models.DateField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(
        max_length=12,
        choices=ShiftStatus.choices,
        default=ShiftStatus.SCHEDULED
    )
    observations = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_employee_shifts"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Programación de turno"
        verbose_name_plural = "Programaciones de turnos"
        ordering = ["work_date", "start_datetime"]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_datetime__gt=models.F("start_datetime")),
                name="employee_shift_end_after_start"
            )
        ]

    def __str__(self):
        return f"{self.employee} - {self.work_date}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.end_datetime <= self.start_datetime:
            raise ValidationError(
                {"end_datetime": "La hora de finalización debe ser posterior al inicio."}
            )
