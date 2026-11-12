from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.core.models import Hotel
from apps.staff.models import Employee


class EventSpace(models.Model):
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.PROTECT,
        related_name="event_spaces"
    )
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=150, blank=True)
    capacity = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    has_audio_visual = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Espacio para eventos"
        verbose_name_plural = "Espacios para eventos"
        ordering = ["hotel", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["hotel", "name"],
                name="unique_event_space_per_hotel"
            ),
            models.CheckConstraint(
                condition=Q(capacity__gt=0),
                name="event_space_capacity_positive"
            ),
        ]

    def __str__(self):
        return f"{self.name} - {self.hotel.name}"


class Event(models.Model):

    class EventType(models.TextChoices):
        WEDDING = "WEDDING", "Boda"
        BANQUET = "BANQUET", "Banquete"
        CONGRESS = "CONGRESS", "Congreso"
        CONVENTION = "CONVENTION", "Convención"
        CORPORATE = "CORPORATE", "Evento corporativo"
        SOCIAL = "SOCIAL", "Evento social"
        OTHER = "OTHER", "Otro"

    class EventStatus(models.TextChoices):
        REQUESTED = "REQUESTED", "Solicitado"
        CONFIRMED = "CONFIRMED", "Confirmado"
        PLANNING = "PLANNING", "En planificación"
        IN_PROGRESS = "IN_PROGRESS", "En ejecución"
        COMPLETED = "COMPLETED", "Finalizado"
        CANCELLED = "CANCELLED", "Cancelado"

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.PROTECT,
        related_name="events"
    )
    space = models.ForeignKey(
        EventSpace,
        on_delete=models.PROTECT,
        related_name="events"
    )
    code = models.CharField(max_length=30)
    title = models.CharField(max_length=180)
    event_type = models.CharField(
        max_length=15,
        choices=EventType.choices
    )
    client_name = models.CharField(max_length=150)
    client_email = models.EmailField(blank=True)
    client_phone = models.CharField(max_length=30, blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    expected_guests = models.PositiveIntegerField()
    status = models.CharField(
        max_length=15,
        choices=EventStatus.choices,
        default=EventStatus.REQUESTED
    )
    special_requirements = models.TextField(blank=True)
    setup_notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_hotel_events"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["start_datetime"]
        constraints = [
            models.UniqueConstraint(
                fields=["hotel", "code"],
                name="unique_event_code_per_hotel"
            ),
            models.CheckConstraint(
                condition=Q(end_datetime__gt=models.F("start_datetime")),
                name="event_end_after_start"
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.title}"

    def clean(self):
        if self.end_datetime and self.start_datetime:
            if self.end_datetime <= self.start_datetime:
                raise ValidationError({
                    "end_datetime": "La finalización debe ser posterior al inicio."
                })

        if self.space_id and self.hotel_id:
            if self.space.hotel_id != self.hotel_id:
                raise ValidationError({
                    "space": "El espacio debe pertenecer al mismo hotel del evento."
                })

            if self.expected_guests > self.space.capacity:
                raise ValidationError({
                    "expected_guests": (
                        "La cantidad de invitados supera la capacidad del espacio."
                    )
                })


class EventStaffAssignment(models.Model):

    class AssignmentStatus(models.TextChoices):
        ASSIGNED = "ASSIGNED", "Asignado"
        CONFIRMED = "CONFIRMED", "Confirmado"
        IN_PROGRESS = "IN_PROGRESS", "En servicio"
        COMPLETED = "COMPLETED", "Finalizado"
        CANCELLED = "CANCELLED", "Cancelado"

    event = models.ForeignKey(
        Event,
        on_delete=models.PROTECT,
        related_name="staff_assignments"
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="event_assignments"
    )
    assigned_role = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(
        max_length=15,
        choices=AssignmentStatus.choices,
        default=AssignmentStatus.ASSIGNED
    )
    observations = models.TextField(blank=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_event_assignments"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Asignación de personal a evento"
        verbose_name_plural = "Asignaciones de personal a eventos"
        ordering = ["start_datetime"]
        constraints = [
            models.UniqueConstraint(
                fields=["event", "employee"],
                name="unique_employee_per_event"
            ),
            models.CheckConstraint(
                condition=Q(end_datetime__gt=models.F("start_datetime")),
                name="event_assignment_end_after_start"
            ),
        ]

    def __str__(self):
        return f"{self.employee} - {self.event.code}"

    def clean(self):
        if self.end_datetime <= self.start_datetime:
            raise ValidationError({
                "end_datetime": "La finalización debe ser posterior al inicio."
            })

        if self.event_id and self.employee_id:
            if self.event.hotel_id != self.employee.hotel_id:
                raise ValidationError(
                    "El empleado debe pertenecer al hotel que organiza el evento."
                )

            if self.employee.employment_status != Employee.EmploymentStatus.ACTIVE:
                raise ValidationError(
                    "Solo se puede asignar personal con estado laboral activo."
                )

            overlapping = EventStaffAssignment.objects.filter(
                employee_id=self.employee_id,
                start_datetime__lt=self.end_datetime,
                end_datetime__gt=self.start_datetime,
            ).exclude(status=self.AssignmentStatus.CANCELLED)

            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)

            if overlapping.exists():
                raise ValidationError(
                    "El empleado ya tiene otra asignación en ese horario."
                )
