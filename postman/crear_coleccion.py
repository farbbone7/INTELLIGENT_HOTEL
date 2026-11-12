import json
from pathlib import Path

base = "{{base_url}}"
auth = "{{access_token}}"

def request(name, method, path, body=None, authenticated=True, tests=None):
    item = {
        "name": name,
        "request": {
            "method": method,
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "url": base + path
        }
    }
    if authenticated:
        item["request"]["auth"] = {
            "type": "bearer",
            "bearer": [{"key": "token", "value": auth, "type": "string"}]
        }
    else:
        item["request"]["auth"] = {"type": "noauth"}
    if body is not None:
        item["request"]["body"] = {
            "mode": "raw",
            "raw": json.dumps(body, ensure_ascii=False, indent=2),
            "options": {"raw": {"language": "json"}}
        }
    if tests:
        item["event"] = [{
            "listen": "test",
            "script": {"type": "text", "exec": tests}
        }]
    return item

def folder(name, items):
    return {"name": name, "item": items}

auth_folder = folder("01 - Autenticación JWT", [
    request(
        "Iniciar sesión",
        "POST",
        "/api/auth/login/",
        {"email": "{{email}}", "password": "{{password}}"},
        False,
        [
            "pm.test('Login responde correctamente', function () {",
            "    pm.response.to.have.status(200);",
            "});",
            "if (pm.response.code === 200) {",
            "    const data = pm.response.json();",
            "    if (data.access) pm.collectionVariables.set('access_token', data.access);",
            "    if (data.refresh) pm.collectionVariables.set('refresh_token', data.refresh);",
            "}"
        ]
    ),
    request(
        "Consultar usuario autenticado",
        "GET",
        "/api/auth/me/"
    ),
    request(
        "Renovar token",
        "POST",
        "/api/auth/refresh/",
        {"refresh": "{{refresh_token}}"},
        False,
        [
            "pm.test('Renovación de token correcta', function () {",
            "    pm.response.to.have.status(200);",
            "});",
            "if (pm.response.code === 200) {",
            "    const data = pm.response.json();",
            "    if (data.access) pm.collectionVariables.set('access_token', data.access);",
            "}"
        ]
    )
])

core = folder("02 - Hoteles y áreas", [
    request("Listar hoteles", "GET", "/api/core/hotels/"),
    request("Consultar hotel por ID", "GET", "/api/core/hotels/{{hotel_id}}/"),
    request("Crear hotel", "POST", "/api/core/hotels/", {
        "name": "Hotel Demo Intelligent",
        "commercial_name": "Intelligent Hotel Demo",
        "category": "4",
        "tax_id": "900000000-1",
        "email": "demo@example.com",
        "phone": "3000000000",
        "address": "Carrera 10 # 20-30",
        "city": "Bogotá",
        "country": "Colombia",
        "timezone": "America/Bogota",
        "is_active": True
    }),
    request("Listar áreas operativas", "GET", "/api/core/areas/"),
    request("Consultar área por ID", "GET", "/api/core/areas/{{area_id}}/"),
    request("Crear área operativa", "POST", "/api/core/areas/", {
        "hotel_id": "{{hotel_id}}",
        "code": "DEMO",
        "name": "Área de demostración",
        "area_type": "OTHER",
        "description": "Área creada para pruebas de API",
        "is_active": True
    })
])

staff = folder("03 - Personal y turnos", [
    request("Listar cargos", "GET", "/api/staff/positions/"),
    request("Crear cargo", "POST", "/api/staff/positions/", {
        "name": "Mesero de demostración",
        "description": "Cargo para pruebas",
        "is_active": True
    }),
    request("Listar turnos", "GET", "/api/staff/shifts/"),
    request("Crear turno", "POST", "/api/staff/shifts/", {
        "name": "Turno demostración",
        "start_time": "07:00:00",
        "end_time": "15:00:00",
        "break_minutes": 30,
        "description": "Turno de prueba",
        "is_active": True
    }),
    request("Listar empleados", "GET", "/api/staff/employees/"),
    request("Consultar empleado", "GET", "/api/staff/employees/{{employee_id}}/"),
    request("Crear empleado", "POST", "/api/staff/employees/", {
        "hotel_id": "{{hotel_id}}",
        "area_id": "{{area_id}}",
        "position_id": "{{position_id}}",
        "employee_code": "DEMO-001",
        "document_number": "1000000001",
        "first_name": "Empleado",
        "last_name": "Demostración",
        "email": "empleado.demo@example.com",
        "phone": "3000000001",
        "hire_date": "2026-01-15",
        "employment_status": "ACTIVE"
    }),
    request("Listar programación de turnos", "GET", "/api/staff/employee-shifts/"),
    request("Crear programación de turno", "POST", "/api/staff/employee-shifts/", {
        "employee_id": "{{employee_id}}",
        "shift_id": "{{shift_id}}",
        "work_date": "2027-01-15",
        "start_datetime": "2027-01-15T07:00:00-05:00",
        "end_datetime": "2027-01-15T15:00:00-05:00",
        "status": "SCHEDULED",
        "observations": "Programación de demostración"
    })
])

events = folder("04 - Espacios y eventos", [
    request("Listar espacios", "GET", "/api/events/spaces/"),
    request("Crear espacio", "POST", "/api/events/spaces/", {
        "hotel_id": "{{hotel_id}}",
        "name": "Salón de demostración",
        "location": "Primer piso",
        "capacity": 100,
        "description": "Espacio para pruebas",
        "has_audio_visual": True,
        "is_active": True
    }),
    request("Listar eventos", "GET", "/api/events/events/"),
    request("Consultar evento", "GET", "/api/events/events/{{event_id}}/"),
    request("Crear evento", "POST", "/api/events/events/", {
        "hotel_id": "{{hotel_id}}",
        "space_id": "{{space_id}}",
        "code": "EVT-DEMO-001",
        "title": "Evento de demostración",
        "event_type": "CORPORATE",
        "client_name": "Cliente de prueba",
        "client_email": "cliente.demo@example.com",
        "client_phone": "3000000002",
        "start_datetime": "2027-02-15T09:00:00-05:00",
        "end_datetime": "2027-02-15T17:00:00-05:00",
        "expected_guests": 50,
        "status": "REQUESTED",
        "special_requirements": "",
        "setup_notes": "Montaje de prueba"
    }),
    request("Listar asignaciones de personal", "GET", "/api/events/assignments/"),
    request("Crear asignación de personal", "POST", "/api/events/assignments/", {
        "event_id": "{{event_id}}",
        "employee_id": "{{employee_id}}",
        "assigned_role": "Mesero",
        "start_datetime": "2027-02-15T09:00:00-05:00",
        "end_datetime": "2027-02-15T17:00:00-05:00",
        "status": "ASSIGNED",
        "observations": "Asignación de demostración"
    })
])

services = folder("05 - Servicios y solicitudes", [
    request("Listar tipos de servicio", "GET", "/api/services/types/"),
    request("Crear tipo de servicio", "POST", "/api/services/types/", {
        "hotel": "{{hotel_id}}",
        "area": "{{area_id}}",
        "code": "SRV-DEMO",
        "name": "Servicio de demostración",
        "category": "ROOM_SERVICE",
        "description": "Tipo de servicio para pruebas",
        "target_minutes": 30,
        "is_active": True
    }),
    request("Listar solicitudes", "GET", "/api/services/requests/"),
    request("Consultar solicitud", "GET", "/api/services/requests/{{request_id}}/"),
    request("Crear solicitud", "POST", "/api/services/requests/", {
        "hotel": "{{hotel_id}}",
        "service_type": "{{service_type_id}}",
        "guest_name": "Huésped de demostración",
        "room_number": "501",
        "contact_phone": "3000000003",
        "description": "Solicitud creada para probar la API",
        "priority": "MEDIUM",
        "channel": "RECEPTION",
        "assigned_area": "{{area_id}}"
    }),
    request("Consultar historial de solicitudes", "GET", "/api/services/history/")
])

operations = folder("06 - Operaciones e incidentes", [
    request("Listar tareas operativas", "GET", "/api/operations/tasks/"),
    request("Consultar tarea", "GET", "/api/operations/tasks/{{task_id}}/"),
    request("Crear tarea operativa", "POST", "/api/operations/tasks/", {
        "hotel": "{{hotel_id}}",
        "area": "{{area_id}}",
        "title": "Preparar salón de eventos",
        "description": "Organizar mobiliario y verificar montaje",
        "priority": "MEDIUM",
        "status": "PENDING",
        "assigned_employee": "{{employee_id}}",
        "due_at": "2027-02-14T18:00:00-05:00"
    }),
    request("Listar incidentes", "GET", "/api/operations/incidents/"),
    request("Consultar incidente", "GET", "/api/operations/incidents/{{incident_id}}/"),
    request("Crear incidente", "POST", "/api/operations/incidents/", {
        "hotel": "{{hotel_id}}",
        "area": "{{area_id}}",
        "title": "Incidente de demostración",
        "description": "Registro de prueba para validar el endpoint",
        "severity": "LOW",
        "status": "REPORTED",
        "investigation_notes": "",
        "corrective_actions": ""
    })
])

docs = folder("07 - Documentación API", [
    request("Obtener esquema OpenAPI", "GET", "/api/schema/"),
    request("Abrir documentación Swagger", "GET", "/api/docs/", authenticated=False)
])

collection = {
    "info": {
        "name": "INTELLIGENT HOTEL - API REST",
        "description": (
            "Colección de pruebas para la API REST del proyecto Intelligent Hotel. "
            "Incluye autenticación JWT, consultas y ejemplos de creación. "
            "Los POST requieren permisos adecuados y variables con IDs válidos. "
            "Los datos de demostración deben ajustarse a los registros existentes."
        ),
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "auth": {
        "type": "bearer",
        "bearer": [{"key": "token", "value": "{{access_token}}", "type": "string"}]
    },
    "variable": [
        {"key": "base_url", "value": "http://127.0.0.1:8000"},
        {"key": "email", "value": "REEMPLAZAR_CORREO"},
        {"key": "password", "value": "REEMPLAZAR_CONTRASENA"},
        {"key": "access_token", "value": ""},
        {"key": "refresh_token", "value": ""},
        {"key": "hotel_id", "value": ""},
        {"key": "area_id", "value": ""},
        {"key": "position_id", "value": ""},
        {"key": "shift_id", "value": ""},
        {"key": "employee_id", "value": ""},
        {"key": "space_id", "value": ""},
        {"key": "event_id", "value": ""},
        {"key": "service_type_id", "value": ""},
        {"key": "request_id", "value": ""},
        {"key": "task_id", "value": ""},
        {"key": "incident_id", "value": ""}
    ],
    "item": [auth_folder, core, staff, events, services, operations, docs]
}

path = Path("postman/INTELLIGENT_HOTEL.postman_collection.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(collection, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Colección creada: {path.resolve()}")
print(f"Solicitudes incluidas: {sum(len(f['item']) for f in collection['item'])}")


