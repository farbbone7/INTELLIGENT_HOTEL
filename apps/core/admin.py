from django.contrib import admin

from .models import Hotel, OperationalArea


class OperationalAreaInline(admin.TabularInline):
    model = OperationalArea
    extra = 1


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "city", "is_active")
    list_filter = ("category", "city", "is_active")
    search_fields = ("name", "commercial_name", "tax_id")
    inlines = [OperationalAreaInline]


@admin.register(OperationalArea)
class OperationalAreaAdmin(admin.ModelAdmin):
    list_display = ("name", "hotel", "area_type", "code", "is_active")
    list_filter = ("hotel", "area_type", "is_active")
    search_fields = ("name", "code", "hotel__name")
