\# TASKFLOW WEB 2.0



\*\*Proyecto Integrador Backend – Módulo 2\*\*



\## 1. Descripción del proyecto



TaskFlow Web 2.0 es una aplicación web desarrollada con Django que permite visualizar y registrar tareas mediante una interfaz sencilla e intuitiva.



Este proyecto corresponde a la evolución de TaskFlow 1.0, desarrollado inicialmente como una aplicación de consola en Python.



\## 2. Tecnologías utilizadas



\- Python 3.13

\- Django 5.2.19

\- HTML5

\- CSS3

\- SQLite

\- PowerShell



\## 3. Funcionalidades implementadas



\- Visualización del listado de tareas.

\- Formulario para crear nuevas tareas.

\- Validación de descripciones vacías.

\- Manejo de solicitudes GET y POST.

\- Protección CSRF en formularios.

\- Navegación entre las páginas.

\- Plantilla base con herencia de templates.

\- Redirección al listado después de enviar correctamente el formulario.



\## 4. Estructura del proyecto



```text

taskflow\_web/

│

├── config/

│   ├── settings.py

│   ├── urls.py

│   ├── asgi.py

│   └── wsgi.py

│

├── tareas/

│   ├── templates/

│   │   └── tareas/

│   │       ├── base.html

│   │       ├── listar.html

│   │       └── crear.html

│   │

│   ├── tests.py

│   ├── urls.py

│   └── views.py

│

├── manage.py

├── requirements.txt

└── README.md

```



\## 5. Instalación y ejecución



\### Crear entorno virtual



```powershell

python -m venv .venv

```



\### Activar entorno virtual



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



\### Instalar dependencias



```powershell

pip install -r requirements.txt

```



\### Aplicar migraciones



```powershell

python manage.py migrate

```



\### Ejecutar el servidor



```powershell

python manage.py runserver

```



\## 6. Acceso a la aplicación



\- Listado de tareas: http://127.0.0.1:8000/tareas/

\- Crear tarea: http://127.0.0.1:8000/tareas/nueva/



\## 7. Pruebas



Para ejecutar las pruebas automatizadas:



```powershell

python manage.py test tareas

```



Se implementaron cuatro pruebas para verificar:



1\. Visualización del listado.

2\. Acceso al formulario de creación.

3\. Validación de descripciones vacías.

4\. Redirección después de enviar una descripción válida.



\*\*Resultado:\*\* 4 pruebas ejecutadas correctamente.



\## 8. Alcance del módulo



En esta versión se implementó la estructura web y el procesamiento de formularios.



La persistencia de las tareas en la base de datos se desarrollará en el siguiente módulo del proyecto.



\---



\*\*Proyecto:\*\* TaskFlow Web 2.0  

\*\*Tecnología principal:\*\* Python y Django  

\*\*Módulo:\*\* 2 – Desarrollo Backend Web

