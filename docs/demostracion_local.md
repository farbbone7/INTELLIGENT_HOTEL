# INTELLIGENT HOTEL
## Guía de demostración local

### 1. Objetivo
Documentar cómo instalar, ejecutar y demostrar localmente la aplicación web INTELLIGENT HOTEL, desarrollada con Python, Django y Django REST Framework.

### 2. Requisitos
- Python 3.13.
- Entorno virtual de Python.
- Dependencias del archivo requirements.txt.
- Base de datos SQLite incluida en el proyecto.

### 3. Preparación del proyecto
Abrir PowerShell en la carpeta raíz del proyecto:

    E:\INTELLIGENT_HOTEL

Activar el entorno virtual:

    .\.venv\Scripts\Activate.ps1

Instalar dependencias si se configura el proyecto en otro equipo:

    pip install -r requirements.txt

### 4. Preparación de la base de datos
Ejecutar las migraciones:

    python manage.py migrate

Si todavía no existe un usuario administrador, crearlo con:

    python manage.py createsuperuser

### 5. Ejecución
Iniciar el servidor de desarrollo:

    python manage.py runserver

Abrir el navegador en:

- Administración: http://127.0.0.1:8000/admin/
- Documentación API: http://127.0.0.1:8000/api/docs/
- Esquema API: http://127.0.0.1:8000/api/schema/

### 6. Módulos de la aplicación
La API está organizada en los siguientes módulos:

- Accounts: usuarios y autenticación.
- Core: funcionalidades centrales.
- Staff: gestión del personal.
- Events: gestión de eventos.
- Services: gestión de servicios.
- Operations: gestión operativa.

### 7. Demostración funcional
Durante la demostración se puede presentar:

1. Inicio de sesión y autenticación.
2. Acceso a la documentación interactiva de la API.
3. Consulta de los endpoints disponibles.
4. Operaciones de consulta y gestión de los módulos.
5. Administración de la aplicación desde Django Admin.

Las operaciones protegidas requieren autenticación y los permisos correspondientes.

### 8. Alcance de la demostración
La aplicación puede ejecutarse localmente para verificar sus funcionalidades. Esta modalidad permite presentar el funcionamiento del backend y sus endpoints sin depender de un servicio de alojamiento externo.

### 9. Repositorio
Código fuente: https://github.com/farbbone7/INTELLIGENT_HOTEL

---
Proyecto académico: INTELLIGENT HOTEL
Tecnologías: Python, Django, Django REST Framework y SQLite.
