
from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_tareas, name='listar'),
    path('nueva/', views.crear_tarea, name='crear'),
]
