from django.contrib import admin

from .models import Event, EventSpace, EventStaffAssignment


@admin.register(EventSpace)
class EventSpaceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "hotel",
        "location",
        "capacity",
        "has_audio_visual",
        "is_active",
    )
    list_filter = ("hotel", "has_audio_visual", "is_active")
    search_fields = ("name", "location", "hotel__name")


class EventStaffAssignmentInline(admin.TabularInline):
    model = EventStaffAssignment
    extra = 0
    autocomplete_fields = ("employee", "assigned_by")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "title",
        "hotel",
        "event_type",
        "space",
        "start_datetime",
        "expected_guests",
        "status",
    )
    list_filter = ("hotel", "event_type", "status")
    search_fields = (
        "code",
        "title",
        "client_name",
        "client_email",
    )
    autocomplete_fields = ("space", "created_by")
    inlines = [EventStaffAssignmentInline]


@admin.register(EventStaffAssignment)
class EventStaffAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "event",
        "employee",
        "assigned_role",
        "start_datetime",
        "end_datetime",
        "status",
    )
    list_filter = ("status", "assigned_role")
    search_fields = (
        "event__code",
        "event__title",
        "employee__first_name",
        "employee__last_name",
        "employee__employee_code",
    )
    autocomplete_fields = ("event", "employee", "assigned_by")
