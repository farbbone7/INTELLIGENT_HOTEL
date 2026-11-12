
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        (
            "Información hotelera",
            {"fields": ("hotel", "role",)}
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Información hotelera",
            {"fields": ("hotel", "role",)}
        ),
    )

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "hotel",
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    list_filter = (
        "hotel",
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "email",
        "username",
        "first_name",
        "last_name",
        "hotel__name",
    )

    ordering = ("email",)
