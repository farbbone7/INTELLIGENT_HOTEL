# Endpoints de la API

Todas las rutas de negocio requieren autenticación JWT, salvo los endpoints de autenticación.

## Autenticación
- POST /api/auth/login/
- POST /api/auth/refresh/
- GET /api/auth/me/

## Core
- /api/core/hotels/
- /api/core/areas/

## Personal
- /api/staff/positions/
- /api/staff/employees/
- /api/staff/shifts/
- /api/staff/employee-shifts/

## Eventos
- /api/events/spaces/
- /api/events/events/
- /api/events/assignments/

## Servicios
- /api/services/types/
- /api/services/requests/
- /api/services/history/

## Operaciones
- /api/operations/tasks/
- /api/operations/incidents/

Los ViewSets exponen las operaciones habilitadas por sus mixins y permisos. Los endpoints de historial son de consulta.

La documentación interactiva y los esquemas de entrada y salida están disponibles en /api/docs/ y /api/schema/.
