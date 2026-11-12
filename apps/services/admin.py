from django.contrib import admin

from .models import ServiceType, ServiceRequest, RequestHistory


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "hotel",
        "area",
        "category",
        "target_minutes",
        "is_active",
    )
    list_filter = (
        "hotel",
        "category",
        "is_active",
    )
    search_fields = (
        "code",
        "name",
        "description",
    )
    ordering = ("hotel", "name")
    list_per_page = 25


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "request_code",
        "guest_name",
        "hotel",
        "service_type",
        "assigned_area",
        "assigned_employee",
        "priority",
        "status",
        "requested_at",
    )
    list_filter = (
        "hotel",
        "status",
        "priority",
        "channel",
        "assigned_area",
    )
    search_fields = (
        "request_code",
        "guest_name",
        "room_number",
        "contact_phone",
        "description",
    )
    readonly_fields = (
        "requested_at",
        "first_response_at",
        "resolved_at",
        "closed_at",
        "created_at",
        "updated_at",
    )
    ordering = ("-requested_at",)
    list_per_page = 25
    list_select_related = (
        "hotel",
        "service_type",
        "assigned_area",
        "assigned_employee",
    )
    date_hierarchy = "requested_at"


@admin.register(RequestHistory)
class RequestHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "request",
        "previous_status",
        "new_status",
        "changed_by",
        "changed_at",
    )
    list_filter = (
        "previous_status",
        "new_status",
        "changed_at",
    )
    search_fields = (
        "request__request_code",
        "request__guest_name",
        "observations",
    )
    readonly_fields = (
        "request",
        "previous_status",
        "new_status",
        "observations",
        "changed_by",
        "changed_at",
    )
    ordering = ("-changed_at",)
    list_per_page = 30
