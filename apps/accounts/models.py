
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador"
        GERENTE = "GERENTE", "Gerente"
        RECEPCION = "RECEPCION", "Recepción"
        SUPERVISOR = "SUPERVISOR", "Supervisor operativo"
        COORDINADOR_EVENTOS = "COORDINADOR_EVENTOS", "Coordinador de eventos"
        PERSONAL_OPERATIVO = "PERSONAL_OPERATIVO", "Personal operativo"

    email = models.EmailField(
        unique=True,
        verbose_name="Correo electrónico"
    )

    hotel = models.ForeignKey(
        "core.Hotel",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users",
        verbose_name="Hotel asignado",
        help_text="Obligatorio para usuarios normales. El superusuario general puede dejarlo vacío."
    )

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.PERSONAL_OPERATIVO,
        verbose_name="Rol del usuario"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def clean(self):
        super().clean()

        if not self.is_superuser and not self.hotel_id:
            raise ValidationError({
                "hotel": "Los usuarios normales deben estar asociados a un hotel."
            })
