from django.db import models


class Hotel(models.Model):

    class Category(models.TextChoices):
        FOUR_STARS = "4", "4 estrellas"
        FIVE_STARS = "5", "5 estrellas"

    name = models.CharField(max_length=150, verbose_name="Nombre del hotel")
    commercial_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nombre comercial"
    )
    category = models.CharField(
        max_length=1,
        choices=Category.choices,
        verbose_name="Categoría"
    )
    tax_id = models.CharField(max_length=30, blank=True, verbose_name="NIT")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Colombia")
    timezone = models.CharField(max_length=60, default="America/Bogota")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hotel"
        verbose_name_plural = "Hoteles"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class OperationalArea(models.Model):

    class AreaType(models.TextChoices):
        RECEPTION = "RECEPTION", "Recepción"
        RESTAURANT = "RESTAURANT", "Restaurante"
        BAR = "BAR", "Bar"
        KITCHEN = "KITCHEN", "Cocina"
        HOUSEKEEPING = "HOUSEKEEPING", "Habitaciones y housekeeping"
        MAINTENANCE = "MAINTENANCE", "Mantenimiento"
        EVENTS = "EVENTS", "Eventos y banquetes"
        ROOM_SERVICE = "ROOM_SERVICE", "Room service"
        CONCIERGE = "CONCIERGE", "Conserjería"
        SECURITY = "SECURITY", "Seguridad"
        OTHER = "OTHER", "Otra área"

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="operational_areas"
    )
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    area_type = models.CharField(
        max_length=25,
        choices=AreaType.choices,
        default=AreaType.OTHER
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Área operativa"
        verbose_name_plural = "Áreas operativas"
        ordering = ["hotel", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["hotel", "code"],
                name="unique_area_code_per_hotel"
            )
        ]

    def __str__(self):
        return f"{self.hotel.name} - {self.name}"
