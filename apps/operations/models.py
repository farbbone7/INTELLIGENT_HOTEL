from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import Hotel, OperationalArea
from apps.events.models import Event
from apps.services.models import ServiceRequest
from apps.staff.models import Employee


class OperationalTask(models.Model):

    class Priority(models.TextChoices):
        LOW = "LOW", "Baja"
        MEDIUM = "MEDIUM", "Media"
        HIGH = "HIGH", "Alta"
        CRITICAL = "CRITICAL", "Crítica"

    class TaskStatus(models.TextChoices):
        PENDING = "PENDING", "Pendiente"
        ASSIGNED = "ASSIGNED", "Asignada"
        IN_PROGRESS = "IN_PROGRESS", "En ejecución"
        ON_HOLD = "ON_HOLD", "En espera"
        COMPLETED = "COMPLETED", "Finalizada"
        CANCELLED = "CANCELLED", "Cancelada"

    hotel = models.ForeignKey(
        Hotel, on_delete=models.PROTECT, related_name="operational_tasks"
    )
    area = models.ForeignKey(
        OperationalArea, on_delete=models.PROTECT, related_name="operational_tasks"
    )
    service_request = models.ForeignKey(
        ServiceRequest, on_delete=models.PROTECT, null=True, blank=True,
        related_name="operational_tasks"
    )
    event = models.ForeignKey(
        Event, on_delete=models.PROTECT, null=True, blank=True,
        related_name="operational_tasks"
    )
    code = models.CharField(max_length=35)
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    status = models.CharField(
        max_length=15, choices=TaskStatus.choices, default=TaskStatus.PENDING
    )
    assigned_employee = models.ForeignKey(
        Employee, on_delete=models.PROTECT, null=True, blank=True,
        related_name="operational_tasks"
    )
    due_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completion_notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="created_operational_tasks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tarea operativa"
        verbose_name_plural = "Tareas operativas"
        ordering = ["due_at", "-priority"]
        constraints = [
            models.UniqueConstraint(
                fields=["hotel", "code"],
                name="unique_operational_task_code"
            ),
        ]
        indexes = [
            models.Index(
                fields=["hotel", "status", "priority"],
                name="task_hotel_status_priority_idx"
            ),
            models.Index(
                fields=["assigned_employee", "status"],
                name="task_employee_status_idx"
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.title}"

    def clean(self):
        if self.area_id and self.hotel_id:
            if self.area.hotel_id != self.hotel_id:
                raise ValidationError(
                    {"area": "El área debe pertenecer al hotel de la tarea."}
                )

        if self.service_request_id and self.hotel_id:
            if self.service_request.hotel_id != self.hotel_id:
                raise ValidationError(
                    "La solicitud debe pertenecer al hotel de la tarea."
                )

        if self.event_id and self.hotel_id:
            if self.event.hotel_id != self.hotel_id:
                raise ValidationError(
                    "El evento debe pertenecer al hotel de la tarea."
                )

        if self.assigned_employee_id and self.hotel_id:
            if self.assigned_employee.hotel_id != self.hotel_id:
                raise ValidationError(
                    "El empleado debe pertenecer al hotel de la tarea."
                )


class Incident(models.Model):

    class Severity(models.TextChoices):
        LOW = "LOW", "Leve"
        MODERATE = "MODERATE", "Moderada"
        HIGH = "HIGH", "Alta"
        CRITICAL = "CRITICAL", "Crítica"

    class IncidentStatus(models.TextChoices):
        REPORTED = "REPORTED", "Reportado"
        INVESTIGATING = "INVESTIGATING", "En investigación"
        ACTION_PLAN = "ACTION_PLAN", "Plan de acción"
        RESOLVED = "RESOLVED", "Resuelto"
        CLOSED = "CLOSED", "Cerrado"

    hotel = models.ForeignKey(
        Hotel, on_delete=models.PROTECT, related_name="incidents"
    )
    area = models.ForeignKey(
        OperationalArea, on_delete=models.PROTECT, related_name="incidents"
    )
    service_request = models.ForeignKey(
        ServiceRequest, on_delete=models.PROTECT, null=True, blank=True,
        related_name="incidents"
    )
    event = models.ForeignKey(
        Event, on_delete=models.PROTECT, null=True, blank=True,
        related_name="incidents"
    )
    employee = models.ForeignKey(
        Employee, on_delete=models.PROTECT, null=True, blank=True,
        related_name="reported_incidents"
    )
    code = models.CharField(max_length=35)
    title = models.CharField(max_length=180)
    description = models.TextField()
    severity = models.CharField(
        max_length=12, choices=Severity.choices, default=Severity.MODERATE
    )
    status = models.CharField(
        max_length=15, choices=IncidentStatus.choices, default=IncidentStatus.REPORTED
    )
    reported_at = models.DateTimeField(auto_now_add=True)
    investigation_notes = models.TextField(blank=True)
    corrective_actions = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="reported_hotel_incidents"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Incidente operativo"
        verbose_name_plural = "Incidentes operativos"
        ordering = ["-reported_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["hotel", "code"],
                name="unique_incident_code_per_hotel"
            ),
        ]
        indexes = [
            models.Index(
                fields=["hotel", "status", "severity"],
                name="incident_status_severity_idx"
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.title}"

    def clean(self):
        if self.area_id and self.hotel_id:
            if self.area.hotel_id != self.hotel_id:
                raise ValidationError(
                    "El área debe pertenecer al hotel del incidente."
                )

        if self.service_request_id and self.hotel_id:
            if self.service_request.hotel_id != self.hotel_id:
                raise ValidationError(
                    "La solicitud debe pertenecer al hotel del incidente."
                )

        if self.event_id and self.hotel_id:
            if self.event.hotel_id != self.hotel_id:
                raise ValidationError(
                    "El evento debe pertenecer al hotel del incidente."
                )

        if self.employee_id and self.hotel_id:
            if self.employee.hotel_id != self.hotel_id:
                raise ValidationError(
                    "El empleado debe pertenecer al hotel del incidente."
                )
