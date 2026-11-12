from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase

from apps.core.models import Hotel, OperationalArea
from apps.staff.models import Position, Employee
from apps.operations.models import OperationalTask, Incident


User = get_user_model()


class OperationsAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        hotel_category = Hotel._meta.get_field("category").choices[0][0]
        area_type = OperationalArea._meta.get_field("area_type").choices[0][0]

        cls.hotel_a = Hotel.objects.create(
            name="Hotel Prueba A",
            category=hotel_category,
            address="Calle 10 # 10-10",
            city="Bogotá",
        )

        cls.hotel_b = Hotel.objects.create(
            name="Hotel Prueba B",
            category=hotel_category,
            address="Carrera 20 # 20-20",
            city="Bogotá",
        )

        cls.area_a = OperationalArea.objects.create(
            hotel=cls.hotel_a,
            code="REC-A",
            name="Recepción",
            area_type=area_type,
        )

        cls.area_b = OperationalArea.objects.create(
            hotel=cls.hotel_b,
            code="REC-B",
            name="Recepción",
            area_type=area_type,
        )

        cls.position = Position.objects.create(
            name="Auxiliar operativo de pruebas"
        )

        cls.manager = cls.create_user(
            "gerente_a@test.com", "GERENTE", cls.hotel_a
        )

        cls.reception = cls.create_user(
            "recepcion_a@test.com", "RECEPCION", cls.hotel_a
        )

        cls.operational_user = cls.create_user(
            "operativo_a@test.com", "PERSONAL_OPERATIVO", cls.hotel_a
        )

        cls.other_manager = cls.create_user(
            "gerente_b@test.com", "GERENTE", cls.hotel_b
        )

        cls.employee = Employee.objects.create(
            hotel=cls.hotel_a,
            user=cls.operational_user,
            employee_code="EMP-001",
            document_number="100000001",
            first_name="Empleado",
            last_name="Prueba",
            position=cls.position,
            area=cls.area_a,
            hire_date=date.today(),
            employment_status="ACTIVE",
        )

    @classmethod
    def create_user(cls, email, role, hotel):
        return User.objects.create_user(
            email=email,
            username=email.split("@")[0],
            password="TestPassword123!",
            hotel=hotel,
            role=role,
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)
        self.client.defaults["HTTP_HOST"] = "localhost"

    def test_manager_can_create_operational_task(self):
        self.authenticate(self.manager)

        response = self.client.post(
            "/api/operations/tasks/",
            {
                "area": self.area_a.id,
                "title": "Revisar habitaciones",
                "description": "Inspección operativa de habitaciones.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)

        task = OperationalTask.objects.get()
        self.assertEqual(task.hotel_id, self.hotel_a.id)
        self.assertEqual(task.created_by_id, self.manager.id)
        self.assertTrue(task.code.startswith("TAR-"))

    def test_hotel_cannot_list_other_hotel_tasks(self):
        task = OperationalTask.objects.create(
            hotel=self.hotel_b,
            area=self.area_b,
            code="TAR-TEST-B",
            title="Tarea privada del hotel B",
            created_by=self.other_manager,
        )

        self.authenticate(self.manager)

        response = self.client.get("/api/operations/tasks/")

        self.assertEqual(response.status_code, 200, response.data)

        results = response.data.get("results", response.data)
        returned_ids = [item["id"] for item in results]

        self.assertNotIn(task.id, returned_ids)

    def test_hotel_cannot_retrieve_other_hotel_task(self):
        task = OperationalTask.objects.create(
            hotel=self.hotel_b,
            area=self.area_b,
            code="TAR-TEST-DETAIL",
            title="Tarea de otro hotel",
            created_by=self.other_manager,
        )

        self.authenticate(self.manager)

        response = self.client.get(
            f"/api/operations/tasks/{task.id}/"
        )

        self.assertEqual(response.status_code, 404)

    def test_reception_can_report_incident(self):
        self.authenticate(self.reception)

        response = self.client.post(
            "/api/operations/incidents/",
            {
                "area": self.area_a.id,
                "title": "Falla en equipo",
                "description": "Se reporta una falla durante la operación.",
                "severity": "MODERATE",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)

        incident = Incident.objects.get()

        self.assertEqual(incident.hotel_id, self.hotel_a.id)
        self.assertEqual(incident.area_id, self.area_a.id)
        self.assertEqual(incident.reported_by_id, self.reception.id)
        self.assertEqual(incident.status, "REPORTED")
        self.assertTrue(incident.code.startswith("INC-"))

    def test_operational_employee_can_report_incident_with_automatic_area(self):
        self.authenticate(self.operational_user)

        response = self.client.post(
            "/api/operations/incidents/",
            {
                "title": "Novedad operativa",
                "description": "Incidente reportado por el colaborador.",
                "severity": "MODERATE",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)

        incident = Incident.objects.get()

        self.assertEqual(incident.hotel_id, self.hotel_a.id)
        self.assertEqual(incident.employee_id, self.employee.id)
        self.assertEqual(incident.area_id, self.area_a.id)
        self.assertEqual(incident.reported_by_id, self.operational_user.id)

    def test_reception_cannot_update_incident(self):
        incident = Incident.objects.create(
            hotel=self.hotel_a,
            area=self.area_a,
            code="INC-TEST-001",
            title="Incidente existente",
            description="Incidente para probar permisos.",
            severity="MODERATE",
            reported_by=self.reception,
        )

        self.authenticate(self.reception)

        response = self.client.patch(
            f"/api/operations/incidents/{incident.id}/",
            {"title": "Intento de modificación"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

        incident.refresh_from_db()
        self.assertEqual(incident.title, "Incidente existente")

    def test_anonymous_user_cannot_access_operations(self):
        self.client.defaults["HTTP_HOST"] = "localhost"

        task_response = self.client.get("/api/operations/tasks/")
        incident_response = self.client.get("/api/operations/incidents/")

        self.assertEqual(task_response.status_code, 401)
        self.assertEqual(incident_response.status_code, 401)
