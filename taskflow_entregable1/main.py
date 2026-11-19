from gestor_tareas import GestorTareas


def pedir_entero(mensaje):
    """Solicita un número entero y controla entradas inválidas."""
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("Error: ingrese un número entero válido.")


def mostrar_menu():
    print("\n" + "=" * 45)
    print("                 TASKFLOW 1.0")
    print("          SISTEMA DE GESTIÓN DE TAREAS")
    print("=" * 45)
    print("1. Agregar tarea")
    print("2. Ver todas las tareas")
    print("3. Marcar tarea como completada")
    print("4. Eliminar tarea")
    print("5. Consultar estadísticas")
    print("6. Salir y guardar información")
    print("=" * 45)


def ejecutar():
    gestor = GestorTareas()

    print("\nBienvenido a TaskFlow 1.0")
    print("Información de tareas cargada correctamente.")

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción (1-6): ").strip()

        if opcion == "1":
            descripcion = input(
                "Ingrese la descripción de la tarea: "
            ).strip()

            if not descripcion:
                print("Error: la descripción no puede estar vacía.")
            else:
                gestor.agregar(descripcion)

        elif opcion == "2":
            gestor.listar()

        elif opcion == "3":
            gestor.listar()

            if gestor.tareas:
                id_tarea = pedir_entero("Ingrese el ID de la tarea: ")
                gestor.completar(id_tarea)

        elif opcion == "4":
            gestor.listar()

            if gestor.tareas:
                id_tarea = pedir_entero("Ingrese el ID que desea eliminar: ")
                gestor.eliminar(id_tarea)

        elif opcion == "5":
            gestor.estadisticas()

        elif opcion == "6":
            if gestor.guardar():
                print("Información guardada correctamente.")
            print("Gracias por utilizar TaskFlow 1.0.")
            break

        else:
            print("Opción no válida. Seleccione un número del 1 al 6.")


if __name__ == "__main__":
    try:
        ejecutar()
    except (KeyboardInterrupt, EOFError):
        print("\nEjecución interrumpida. Hasta pronto.")