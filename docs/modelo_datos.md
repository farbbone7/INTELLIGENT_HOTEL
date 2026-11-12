# Modelo de datos

## Entidades principales

- Hotel: unidad hotelera y ámbito de aislamiento de información.
- OperationalArea: áreas operativas pertenecientes a un hotel.
- User: usuario autenticado con rol y hotel asociado.
- Position: catálogo de cargos.
- Employee: trabajador asociado a hotel, área y cargo.
- Shift: catálogo de turnos.
- EmployeeShift: programación de turnos del personal.
- EventSpace: espacios disponibles para eventos.
- Event: eventos y datos de organización.
- EventStaffAssignment: asignación de trabajadores a eventos.
- ServiceType: catálogo de servicios por hotel y área.
- ServiceRequest: solicitudes de huéspedes o áreas internas.
- RequestHistory: trazabilidad de cambios de estado.
- OperationalTask: tareas de operación.
- Incident: novedades e incidentes operativos.

## Relaciones

- Un hotel tiene múltiples áreas, empleados, eventos y solicitudes.
- Un área pertenece a un hotel.
- Un empleado pertenece a un hotel y puede asociarse a un usuario.
- Un empleado puede tener múltiples asignaciones de turno.
- Un evento pertenece a un hotel y puede ocupar un espacio.
- Un evento puede tener varias asignaciones de personal.
- Una solicitud pertenece a un hotel y registra su historial.
- Una tarea o incidente puede relacionarse con un área, empleado, evento o solicitud.

Las restricciones de integridad y las relaciones específicas se encuentran definidas en los modelos y migraciones de cada aplicación.
