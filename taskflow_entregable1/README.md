\# TaskFlow 1.0



\## Descripción

TaskFlow es una aplicación de consola desarrollada en Python para gestionar tareas de manera sencilla y organizada.



\## Funcionalidades

\- Agregar tareas.

\- Consultar todas las tareas y sus estados.

\- Marcar tareas como completadas.

\- Eliminar tareas.

\- Consultar estadísticas de tareas pendientes y completadas.

\- Guardar y recuperar información mediante archivos JSON.



\## Tecnologías

\- Python 3.

\- Biblioteca estándar de Python.

\- JSON para persistencia de información.



\## Estructura del proyecto



taskflow\_entregable1/

├── main.py

├── modelos.py

├── gestor\_tareas.py

├── README.md

└── data/

&#x20;   └── tareas.json



\## Ejecución

Desde esta carpeta ejecutar:



python main.py



\## Persistencia

Las tareas se almacenan en data/tareas.json y se recuperan automáticamente al iniciar el programa.



\## Manejo de errores

El programa valida las opciones del menú, los números ingresados y las descripciones vacías. También controla errores de lectura y escritura del archivo JSON.

