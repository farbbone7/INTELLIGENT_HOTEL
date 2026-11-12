# Instalación y ejecución

## Requisitos

- Python 3.13.
- pip.
- PowerShell en Windows.

## Instalación local

Desde la carpeta raíz del proyecto:

1. Crear el entorno virtual:

   `python -m venv .venv`

2. Activarlo:

   `.\.venv\Scripts\Activate.ps1`

3. Instalar dependencias:

   `python -m pip install -r requirements.txt`

4. Crear el archivo de configuración:

   `Copy-Item .env.example .env`

5. Editar `.env` y configurar una SECRET_KEY privada.

6. Aplicar las migraciones:

   `python manage.py migrate`

7. Crear el usuario administrador:

   `python manage.py createsuperuser`

8. Iniciar el servidor:

   `python manage.py runserver`

## Accesos locales

- API: http://127.0.0.1:8000/
- Swagger: http://127.0.0.1:8000/api/docs/
- Esquema OpenAPI: http://127.0.0.1:8000/api/schema/
- Administración: http://127.0.0.1:8000/admin/

## Verificación

- `python manage.py check`
- `python manage.py test -v 2`
- `python manage.py makemigrations --check --dry-run`

## Base de datos

Se utiliza SQLite para el desarrollo y la demostración local. La base de datos se administra mediante Django ORM y las migraciones del proyecto.

El despliegue en un servidor requiere configurar las variables de entorno, la base de datos y las medidas de seguridad correspondientes al proveedor de alojamiento.
