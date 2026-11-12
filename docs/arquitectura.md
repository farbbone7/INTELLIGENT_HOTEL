# Arquitectura del sistema

INTELLIGENT HOTEL utiliza una arquitectura modular basada en Django y Django REST Framework.

## Capas

- Modelos: representan las entidades y relaciones persistidas mediante Django ORM.
- Serializers: validan y transforman los datos de entrada y salida.
- ViewSets: implementan las operaciones de la API.
- Permissions: controlan el acceso por rol y pertenencia al hotel.
- URLs: publican los recursos REST.
- Base de datos: SQLite en desarrollo.

## Aplicaciones

- accounts: identidad, usuarios y autenticación.
- core: hoteles y áreas.
- staff: empleados, cargos, turnos y asignaciones.
- events: espacios, eventos y personal asignado.
- services: catálogo, solicitudes e historial.
- operations: tareas e incidentes.

## Flujo general

Cliente API -> JWT -> ViewSet -> Permission -> Serializer -> ORM -> Base de datos.

La separación por aplicaciones facilita el mantenimiento y la ampliación futura.
