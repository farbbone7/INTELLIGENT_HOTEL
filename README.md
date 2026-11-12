# INTELLIGENT HOTEL

## Proyecto integrador - Aplicación Back-End

API REST desarrollada con Python, Django y Django REST Framework para apoyar la gestión de procesos operativos en hoteles de cuatro y cinco estrellas.

El sistema permite administrar hoteles, áreas operativas, personal, turnos, espacios y eventos, solicitudes de servicios, tareas e incidentes.

## Tecnologías

- Python 3.13
- Django 5.2
- Django REST Framework 3.16
- Django REST Framework SimpleJWT
- SQLite para desarrollo
- Django Filter
- drf-spectacular para documentación OpenAPI
- WhiteNoise para archivos estáticos

## Arquitectura

El proyecto está organizado por aplicaciones:

| Aplicación | Responsabilidad |
|---|---|
| accounts | Usuarios, roles y autenticación |
| core | Hoteles y áreas operativas |
| staff | Personal, cargos y turnos |
| events | Espacios, eventos y asignación de personal |
| services | Tipos de servicio, solicitudes e historial |
| operations | Tareas operativas e incidentes |

## Requisitos

- Python 3.13 (versión utilizada durante el desarrollo).
- pip.
- PowerShell, terminal o IDE.
- Git para control de versiones.

## Instalación en Windows

1. Clonar o descargar el repositorio.
2. Entrar a la carpeta del proyecto.
3. Crear el entorno virtual:

   `python -m venv .venv`

4. Activar el entorno:

   `.\.venv\Scripts\Activate.ps1`

5. Instalar dependencias:

   `python -m pip install -r requirements.txt`

6. Crear el archivo `.env` a partir de `.env.example`.
7. Configurar una SECRET_KEY propia y los demás valores del entorno.
8. Aplicar migraciones:

   `python manage.py migrate`

9. Crear el administrador inicial:

   `python manage.py createsuperuser`

10. Ejecutar el servidor:

   `python manage.py runserver`

## Ejecución

Servidor local:

`http://127.0.0.1:8000/`

Administración Django:

`http://127.0.0.1:8000/admin/`

Documentación interactiva:

`http://127.0.0.1:8000/api/docs/`

Esquema OpenAPI:

`http://127.0.0.1:8000/api/schema/`

## Autenticación

La API utiliza JSON Web Tokens (JWT).

Obtener tokens:

`POST /api/auth/login/`

Renovar token:

`POST /api/auth/refresh/`

Consultar usuario autenticado:

`GET /api/auth/me/`

Para acceder a los endpoints protegidos, enviar el encabezado:

`Authorization: Bearer <access_token>`

El token de acceso tiene una duración configurada de 30 minutos y el de renovación de un día.

## Endpoints principales

| Módulo | Ruta |
|---|---|
| Autenticación | `/api/auth/` |
| Hoteles | `/api/core/hotels/` |
| Áreas operativas | `/api/core/areas/` |
| Cargos | `/api/staff/positions/` |
| Empleados | `/api/staff/employees/` |
| Turnos | `/api/staff/shifts/` |
| Asignaciones de turnos | `/api/staff/employee-shifts/` |
| Espacios de eventos | `/api/events/spaces/` |
| Eventos | `/api/events/events/` |
| Asignaciones de eventos | `/api/events/assignments/` |
| Tipos de servicio | `/api/services/types/` |
| Solicitudes | `/api/services/requests/` |
| Historial de solicitudes | `/api/services/history/` |
| Tareas | `/api/operations/tasks/` |
| Incidentes | `/api/operations/incidents/` |

Los endpoints de consulta, creación, actualización y eliminación dependen de las operaciones habilitadas en cada ViewSet y de los permisos del usuario. El historial de solicitudes es de solo lectura.

## Roles y seguridad

Se manejan roles de administrador de plataforma, gerente, recepción, supervisor, coordinador de eventos y personal operativo.

La API aplica autenticación, autorización por roles, aislamiento de información por hotel y validación de relaciones entre registros.

Las credenciales y claves se configuran mediante variables de entorno. El archivo `.env` no debe publicarse.

## Pruebas

Ejecutar la suite automatizada:

`python manage.py test -v 2`

Verificar configuración:

`python manage.py check`

Comprobar migraciones:

`python manage.py makemigrations --check --dry-run`

Generar esquema OpenAPI:

`python manage.py spectacular --file schema_integral.yml --validate`

## Base de datos

Se utiliza SQLite en el entorno de desarrollo. Django ORM gestiona las entidades, relaciones, restricciones y migraciones.

## Documentación complementaria

La carpeta `docs/` contiene arquitectura, instalación, modelo de datos, endpoints y seguridad.

## Alcance

Este entregable corresponde al componente Back-End y a su API REST. La interfaz frontend queda prevista para una fase posterior.

La ejecución local permite demostrar el funcionamiento de los servicios. La publicación en una plataforma de despliegue requiere configurar las variables y servicios correspondientes al entorno de destino.

## Uso de herramientas e inteligencia artificial

Se utilizaron documentación técnica oficial, librerías de código abierto y herramientas de asistencia con inteligencia artificial como apoyo al desarrollo, revisión y documentación. El equipo debe verificar y sustentar las decisiones y el código entregado.

## Licencias

Django, Django REST Framework y las demás dependencias conservan sus respectivas licencias de distribución.

