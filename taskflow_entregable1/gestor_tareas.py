import json
from pathlib import Path
from modelos import Tarea


class GestorTareas:
    """Administra las tareas y su almacenamiento."""

    def __init__(self):
        self.archivo = Path(__file__).parent / "data" / "tareas.json"
        self.tareas = []
        self.cargar()

    def cargar(self):
        """Carga las tareas almacenadas en JSON."""
        try:
            if self.archivo.exists():
                with self.archivo.open("r", encoding="utf-8") as archivo:
                    datos = json.load(archivo)

                if not isinstance(datos, list):
                    raise ValueError("El archivo debe contener una lista.")

                self.tareas = [Tarea.from_dict(item) for item in datos]

        except (json.JSONDecodeError, OSError, ValueError, KeyError, TypeError) as error:
            print(f"Advertencia al cargar tareas: {error}")
            self.tareas = []

    def guardar(self):
        """Guarda las tareas en el archivo JSON."""
        try:
            self.archivo.parent.mkdir(parents=True, exist_ok=True)

            datos = [tarea.to_dict() for tarea in self.tareas]

            with self.archivo.open("w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=4)

            return True

        except OSError as error:
            print(f"Error al guardar las tareas: {error}")
            return False

    def agregar(self, descripcion):
        """Registra una nueva tarea."""
        nuevo_id = max(
            (tarea.id for tarea in self.tareas),
            default=0
        ) + 1

        tarea = Tarea(nuevo_id, descripcion)
        self.tareas.append(tarea)

        if self.guardar():
            print(f"Tarea {nuevo_id} creada correctamente.")
        else:
            print("No fue posible guardar la tarea.")

    def listar(self):
        """Muestra todas las tareas."""
        if not self.tareas:
            print("\nNo hay tareas registradas.")
            return

        print("\n--- LISTADO DE TAREAS ---")

        for tarea in self.tareas:
            print(tarea)

    def buscar(self, id_tarea):
        """Busca una tarea mediante su identificador."""
        for tarea in self.tareas:
            if tarea.id == id_tarea:
                return tarea

        return None

    def completar(self, id_tarea):
        """Marca una tarea como completada."""
        tarea = self.buscar(id_tarea)

        if tarea is None:
            print("No existe una tarea con ese ID.")
            return

        if tarea.estado == "Completada":
            print("La tarea ya está completada.")
            return

        tarea.completar()

        if self.guardar():
            print("Tarea completada correctamente.")
        else:
            print("No fue posible guardar el cambio.")

    def eliminar(self, id_tarea):
        """Elimina una tarea."""
        tarea = self.buscar(id_tarea)

        if tarea is None:
            print("No existe una tarea con ese ID.")
            return

        self.tareas.remove(tarea)

        if self.guardar():
            print("Tarea eliminada correctamente.")
        else:
            print("No fue posible guardar el cambio.")

    def estadisticas(self):
        """Calcula las tareas pendientes y completadas."""
        pendientes = sum(
            1 for tarea in self.tareas
            if tarea.estado == "Pendiente"
        )

        completadas = sum(
            1 for tarea in self.tareas
            if tarea.estado == "Completada"
        )

        print("\n--- ESTADÍSTICAS ---")
        print(f"Total de tareas: {len(self.tareas)}")
        print(f"Pendientes: {pendientes}")
        print(f"Completadas: {completadas}")