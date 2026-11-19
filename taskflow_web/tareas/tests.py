
from django.test import TestCase
from django.urls import reverse


class TareasViewsTests(TestCase):

    def test_listar_tareas_responde_correctamente(self):
        response = self.client.get(reverse('listar'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tareas/listar.html')
        self.assertContains(response, 'Listado de tareas')

    def test_formulario_crear_tarea_responde_correctamente(self):
        response = self.client.get(reverse('crear'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tareas/crear.html')
        self.assertContains(response, 'Crear nueva tarea')

    def test_descripcion_vacia_muestra_error(self):
        response = self.client.post(
            reverse('crear'),
            {'descripcion': '   '}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'La descripción no puede estar vacía.'
        )

    def test_descripcion_valida_redirige_al_listado(self):
        response = self.client.post(
            reverse('crear'),
            {'descripcion': 'Preparar entrega del módulo 2'}
        )

        self.assertRedirects(response, reverse('listar'))
