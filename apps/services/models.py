from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.core.models import Hotel, OperationalArea
from apps.staff.models import Employee


class ServiceType(models.Model):

    class Category(models.TextChoices):
        ROOM_SERVICE = "ROOM_SERVICE", "Room service"
        RESTAURANT = "RESTAURANT", "Restaurante"
        BAR = "BAR", "Bar"
        HOUSEKEEPING = "HOUSEKEEPING", "Housekeeping"
        MAINTENANCE = "MAINTENANCE", "Mantenimiento"
        VIP = "VIP", "Atención VIP"
        CONCIERGE = "CONCIERGE", "Conserjería"
        SPECIAL = "SPECIAL", "Solicitud especial"
        OTHER = "OTHER", "Otro"

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.PROTECT,
        related_name="service_types"
    )
    area = models.ForeignKey(
        OperationalArea,
        on_delete=models.PROTECT,
        related_name="service_types"
    )
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=120)
    category = models.CharField(
        max_length=20,
        choices=Category.choices
    )
    description = models.TextField(blank=True)
    target_minutes = models.PositiveIntegerField(
        default=30,
        help_text="Tiempo objetivo de atención en minutos."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tipo de servicio"
        verbose_name_plural = "Tipos de servicio"
        ordering = ["hotel", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["hotel", "code"],
                name="unique_service_type_code_per_hotel"
            ),
            models.CheckConstraint(
                condition=Q(target_minutes__gt=0),
                name="service_target_minutes_positive"
            ),
        ]

    def __str__(self):
        return f"{self.name} - {self.hotel.name}"

    def clean(self):
        if self.area_id and self.hotel_id:
            if self.area.hotel_id != self.hotel_id:
                raise ValidationError({
                    "area": "El área debe pertenecer al hotel del servicio."
                })


class ServiceRequest(models.Model):

    class Priority(models.TextChoices):
        LOW = "LOW", "Baja"
        MEDIUM = "MEDIUM", "Media"
        HIGH = "HIGH", "Alta"
        CRITICAL = "CRITICAL", "Crítica"

    class RequestStatus(models.TextChoices):
        RECEIVED = "RECEIVED", "Recibida"
        ASSIGNED = "ASSIGNED", "Asignada"
        IN_PROGRESS = "IN_PROGRESS", "En atención"
        ON_HOLD = "ON_HOLD", "En espera"
        RESOLVED = "RESOLVED", "Resuelta"
        CLOSED = "CLOSED", "Cerrada"
        CANCELLED = "CANCELLED", "Cancelada"

    class Channel(models.TextChoices):
        RECEPTION = "RECEPTION", "Recepción"
        PHONE = "PHONE", "Teléfono"
        IN_PERSON = "IN_PERSON", "Presencial"
        DIGITAL = "DIGITAL", "Canal digital"
        INTERNAL = "INTERNAL", "Solicitud interna"

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.PROTECT,
        related_name="service_requests"
    )
    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.PROTECT,
        related_name="requests"
    )
    request_code = models.CharField(max_length=35)
    guest_name = models.CharField(max_length=150)
    room_number = models.CharField(max_length=20, blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    description = models.TextField()
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    status = models.CharField(
        max_length=15,
        choices=RequestStatus.choices,
        default=RequestStatus.RECEIVED
    )
    channel = models.CharField(
        max_length=15,
        choices=Channel.choices,
        default=Channel.RECEPTION
    )
    assigned_area = models.ForeignKey(
        OperationalArea,
        on_delete=models.PROTECT,
        related_name="assigned_requests"
    )
    assigned_employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="service_requests"
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    response_deadline = models.DateTimeField(
        null=True,
        blank=True
    )
    first_response_at = models.DateTimeField(
        null=True,
        blank=True
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True
    )
    resolution_notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_service_requests"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_service_requests"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Solicitud de servicio"
        verbose_name_plural = "Solicitudes de servicio"
        ordering = ["-requested_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["hotel", "request_code"],
                name="unique_request_code_per_hotel"
            ),
        ]
        indexes = [
            models.Index(
                fields=["hotel", "status", "priority"],
                name="request_status_priority_idx"
            ),
            models.Index(
                fields=["assigned_employee", "status"],
                name="request_employee_status_idx"
            ),
            models.Index(
                fields=["response_deadline", "status"],
                name="request_deadline_status_idx"
            ),
        ]

    def __str__(self):
        return f"{self.request_code} - {self.guest_name}"

    def clean(self):
        if self.service_type_id and self.hotel_id:
            if self.service_type.hotel_id != self.hotel_id:
                raise ValidationError({
                    "service_type": "El servicio debe pertenecer al hotel."
                })

        if self.assigned_area_id and self.hotel_id:
            if self.assigned_area.hotel_id != self.hotel_id:
                raise ValidationError({
                    "assigned_area": "El área debe pertenecer al hotel."
                })

        if self.assigned_employee_id and self.hotel_id:
            if self.assigned_employee.hotel_id != self.hotel_id:
                raise ValidationError({
                    "assigned_employee": "El empleado debe pertenecer al hotel."
                })

            if self.assigned_employee.employment_status != Employee.EmploymentStatus.ACTIVE:
                raise ValidationError({
                    "assigned_employee": "El empleado no está activo."
                })


class RequestHistory(models.Model):

    request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.PROTECT,
        related_name="history"
    )
    previous_status = models.CharField(
        max_length=15,
        choices=ServiceRequest.RequestStatus.choices,
        blank=True
    )
    new_status = models.CharField(
        max_length=15,
        choices=ServiceRequest.RequestStatus.choices
    )
    observations = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_history"
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historial de solicitud"
        verbose_name_plural = "Historial de solicitudes"
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.request.request_code} - {self.new_status}"
