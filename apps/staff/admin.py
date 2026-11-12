from django.contrib import admin

from .models import Employee, EmployeeShift, Position, Shift


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "employee_code",
        "first_name",
        "last_name",
        "hotel",
        "area",
        "position",
        "employment_status",
    )
    list_filter = ("hotel", "area", "position", "employment_status")
    search_fields = (
        "employee_code",
        "document_number",
        "first_name",
        "last_name",
        "email",
    )
    autocomplete_fields = ("user",)


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("name", "start_time", "end_time", "is_active")
    list_filter = ("is_active",)


@admin.register(EmployeeShift)
class EmployeeShiftAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "shift",
        "work_date",
        "start_datetime",
        "end_datetime",
        "status",
    )
    list_filter = ("work_date", "status", "shift")
    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "employee__employee_code",
    )
    autocomplete_fields = ("employee", "created_by")
