class Tarea:
    """Representa una tarea del sistema TaskFlow."""

    def __init__(self, id, descripcion, estado="Pendiente"):
        self.id = id
        self.descripcion = descripcion
        self.estado = estado

    def completar(self):
        self.estado = "Completada"

    def to_dict(self):
        return {
            "id": self.id,
            "descripcion": self.descripcion,
            "estado": self.estado
        }

    @classmethod
    def from_dict(cls, datos):
        return cls(
            datos["id"],
            datos["descripcion"],
            datos.get("estado", "Pendiente")
        )

    def __str__(self):
        return (
            f"ID: {self.id} | "
            f"Descripción: {self.descripcion} | "
            f"Estado: {self.estado}"
        )