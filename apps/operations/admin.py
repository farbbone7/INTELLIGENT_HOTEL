from django.contrib import admin

from .models import Incident, OperationalTask


@admin.register(OperationalTask)
class OperationalTaskAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "title",
        "hotel",
        "area",
        "assigned_employee",
        "priority",
        "status",
        "due_at",
    )
    list_filter = ("hotel", "area", "priority", "status")
    search_fields = (
        "code",
        "title",
        "assigned_employee__first_name",
        "assigned_employee__last_name",
    )
    autocomplete_fields = (
        "service_request",
        "event",
        "assigned_employee",
        "created_by",
    )


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "title",
        "hotel",
        "area",
        "severity",
        "status",
        "reported_at",
    )
    list_filter = ("hotel", "area", "severity", "status")
    search_fields = ("code", "title", "description")
    autocomplete_fields = (
        "service_request",
        "event",
        "employee",
        "reported_by",
    )
