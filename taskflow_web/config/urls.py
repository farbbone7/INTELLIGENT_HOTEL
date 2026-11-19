
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rutas de la aplicación TaskFlow
    path('tareas/', include('tareas.urls')),
]
