# Seguridad

## Autenticación

La API utiliza JSON Web Tokens (JWT) mediante djangorestframework-simplejwt. Los endpoints protegidos requieren un token de acceso válido.

## Autorización

Los permisos se controlan mediante roles y pertenencia al hotel.

- Administrador de plataforma: acceso global según los permisos definidos.
- Gerente: administración de procesos autorizados de su hotel.
- Supervisor: gestión operativa según sus permisos.
- Coordinador de eventos: gestión autorizada de eventos.
- Recepción: registro y consulta de solicitudes e incidentes permitidos.
- Personal operativo: acceso a las tareas y solicitudes que tiene asignadas, según las reglas implementadas.

## Aislamiento de información

Las consultas y operaciones se restringen al hotel asociado al usuario. Se validan las relaciones entre hoteles, áreas, empleados, eventos y solicitudes para evitar referencias entre hoteles no autorizadas.

## Variables de entorno

La configuración utiliza:

- SECRET_KEY
- DEBUG
- ALLOWED_HOSTS
- LANGUAGE_CODE
- TIME_ZONE

Los valores se leen mediante python-decouple.

El archivo `.env` contiene configuración privada y no debe publicarse. El repositorio incluye únicamente `.env.example`, con valores ilustrativos.

## Recomendaciones para producción

- Generar una SECRET_KEY nueva y privada.
- Establecer DEBUG=False.
- Configurar ALLOWED_HOSTS con los dominios autorizados.
- Utilizar HTTPS.
- Configurar correctamente CORS y cookies seguras.
- Utilizar una base de datos de producción administrada y respaldada.
- Configurar las opciones de seguridad HTTPS de Django según el proveedor de alojamiento.
- No publicar tokens, contraseñas ni datos reales de huéspedes.

## Alcance de seguridad de esta entrega

La configuración actual está preparada para ejecución y demostración local. Antes de publicar el sistema en producción deben aplicarse y verificarse las medidas específicas del entorno de alojamiento.
