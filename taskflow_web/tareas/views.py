
from django.shortcuts import render, redirect


def listar_tareas(request):
    """
    Muestra el listado de tareas.
    Por ahora utilizamos una lista vacía.
    En el módulo 3 conectaremos la base de datos.
    """
    tareas = []

    return render(request, 'tareas/listar.html', {
        'tareas': tareas
    })


def crear_tarea(request):
    """
    Permite crear una tarea mediante un formulario.
    """
    error = None

    if request.method == 'POST':
        descripcion = request.POST.get('descripcion', '').strip()

        if not descripcion:
            error = 'La descripción no puede estar vacía.'
        else:
            # En el módulo 3 guardaremos la tarea en la base de datos.
            return redirect('listar')

    return render(request, 'tareas/crear.html', {
        'error': error
    })
