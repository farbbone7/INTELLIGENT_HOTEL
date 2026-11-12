from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.core.models import Hotel, OperationalArea
from apps.staff.models import Employee, Position
from apps.services.models import ServiceType, ServiceRequest, RequestHistory


User = get_user_model()


class ServicesAPITests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Dos hoteles independientes.
        cls.hotel_a = Hotel.objects.create(
            name="Hotel Prueba A",
            category="5",
            address="Dirección A",
            city="Bogotá",
        )

        cls.hotel_b = Hotel.objects.create(
            name="Hotel Prueba B",
            category="4",
            address="Dirección B",
            city="Bogotá",
        )

        # Áreas de cada hotel.
        cls.area_a = OperationalArea.objects.create(
            hotel=cls.hotel_a,
            code="ROOM-A",
            name="Habitaciones A",
            area_type="HOUSEKEEPING",
        )

        cls.area_b = OperationalArea.objects.create(
            hotel=cls.hotel_b,
            code="ROOM-B",
            name="Habitaciones B",
            area_type="HOUSEKEEPING",
        )

        cls.events_area_a = OperationalArea.objects.create(
            hotel=cls.hotel_a,
            code="EVENT-A",
            name="Eventos A",
            area_type="EVENTS",
        )

        cls.position = Position.objects.create(
            name="Auxiliar de servicio",
        )

        # Usuarios del hotel A.
        cls.gerente = cls.create_user(
            "gerente",
            cls.hotel_a,
            "GERENTE",
        )

        cls.supervisor = cls.create_user(
            "supervisor",
            cls.hotel_a,
            "SUPERVISOR",
        )

        cls.recepcion = cls.create_user(
            "recepcion",
            cls.hotel_a,
            "RECEPCION",
        )

        cls.coordinador = cls.create_user(
            "coordinador",
            cls.hotel_a,
            "COORDINADOR_EVENTOS",
        )

        cls.operativo = cls.create_user(
            "operativo",
            cls.hotel_a,
            "PERSONAL_OPERATIVO",
        )

        cls.operativo_dos = cls.create_user(
            "operativo_dos",
            cls.hotel_a,
            "PERSONAL_OPERATIVO",
        )

        # Usuario del hotel B.
        cls.gerente_b = cls.create_user(
            "gerente_b",
            cls.hotel_b,
            "GERENTE",
        )

        # Perfiles de empleados.
        cls.employee_a = cls.create_employee(
            cls.hotel_a,
            cls.area_a,
            cls.operativo,
            "EMP-A1",
            "100001",
        )

        cls.employee_a_dos = cls.create_employee(
            cls.hotel_a,
            cls.area_a,
            cls.operativo_dos,
            "EMP-A2",
            "100002",
        )

        cls.employee_b = cls.create_employee(
            cls.hotel_b,
            cls.area_b,
            None,
            "EMP-B1",
            "200001",
        )

        # Tipos de servicio.
        cls.service_type_a = ServiceType.objects.create(
            hotel=cls.hotel_a,
            area=cls.area_a,
            code="ROOM-001",
            name="Servicio de habitaciones A",
            category="ROOM_SERVICE",
            target_minutes=30,
        )

        cls.service_type_b = ServiceType.objects.create(
            hotel=cls.hotel_b,
            area=cls.area_b,
            code="ROOM-001",
            name="Servicio de habitaciones B",
            category="ROOM_SERVICE",
            target_minutes=30,
        )

        # Solicitudes de prueba.
        cls.request_a = cls.create_request(
            cls.hotel_a,
            cls.service_type_a,
            cls.area_a,
            cls.employee_a,
            "SOL-A-001",
        )

        cls.request_a_dos = cls.create_request(
            cls.hotel_a,
            cls.service_type_a,
            cls.area_a,
            cls.employee_a_dos,
            "SOL-A-002",
        )

        cls.request_event = cls.create_request(
            cls.hotel_a,
            cls.service_type_a,
            cls.events_area_a,
            None,
            "SOL-A-003",
        )

        cls.request_b = cls.create_request(
            cls.hotel_b,
            cls.service_type_b,
            cls.area_b,
            cls.employee_b,
            "SOL-B-001",
        )

        RequestHistory.objects.create(
            request=cls.request_a,
            previous_status="",
            new_status="RECEIVED",
            observations="Solicitud de prueba.",
            changed_by=cls.recepcion,
        )

        RequestHistory.objects.create(
            request=cls.request_b,
            previous_status="",
            new_status="RECEIVED",
            observations="Solicitud de otro hotel.",
            changed_by=cls.gerente_b,
        )

    @classmethod
    def create_user(cls, username, hotel, role):
        return User.objects.create_user(
            username=username,
            email=f"{username}@example.test",
            password="TestPassword123!",
            hotel=hotel,
            role=role,
        )

    @classmethod
    def create_employee(
        cls,
        hotel,
        area,
        user,
        employee_code,
        document_number,
    ):
        return Employee.objects.create(
            hotel=hotel,
            user=user,
            employee_code=employee_code,
            document_number=document_number,
            first_name="Empleado",
            last_name=employee_code,
            position=cls.position,
            area=area,
            hire_date=date(2026, 1, 1),
            employment_status="ACTIVE",
        )

    @classmethod
    def create_request(
        cls,
        hotel,
        service_type,
        area,
        employee,
        code,
    ):
        return ServiceRequest.objects.create(
            hotel=hotel,
            service_type=service_type,
            request_code=code,
            guest_name="Huésped de prueba",
            description="Solicitud automatizada de prueba.",
            priority="MEDIUM",
            status="RECEIVED",
            channel="RECEPTION",
            assigned_area=area,
            assigned_employee=employee,
        )

    def setUp(self):
        self.client = APIClient()
        self.client.defaults["HTTP_HOST"] = "localhost"

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_hotel_cannot_see_other_hotel_service_types(self):
        self.authenticate(self.gerente)

        response = self.client.get("/api/services/types/")

        self.assertEqual(response.status_code, 200)

        ids = [item["id"] for item in response.data["results"]]

        self.assertIn(self.service_type_a.id, ids)
        self.assertNotIn(self.service_type_b.id, ids)

    def test_hotel_cannot_see_other_hotel_requests(self):
        self.authenticate(self.gerente)

        response = self.client.get("/api/services/requests/")

        self.assertEqual(response.status_code, 200)

        ids = [item["id"] for item in response.data["results"]]

        self.assertIn(self.request_a.id, ids)
        self.assertNotIn(self.request_b.id, ids)

    def test_hotel_cannot_retrieve_other_hotel_request(self):
        self.authenticate(self.gerente)

        response = self.client.get(
            f"/api/services/requests/{self.request_b.id}/"
        )

        self.assertEqual(response.status_code, 404)

    def test_operational_employee_only_sees_assigned_requests(self):
        self.authenticate(self.operativo)

        response = self.client.get("/api/services/requests/")

        self.assertEqual(response.status_code, 200)

        ids = [item["id"] for item in response.data["results"]]

        self.assertIn(self.request_a.id, ids)
        self.assertNotIn(self.request_a_dos.id, ids)
        self.assertNotIn(self.request_b.id, ids)

    def test_operational_employee_cannot_retrieve_other_employee_request(self):
        self.authenticate(self.operativo)

        response = self.client.get(
            f"/api/services/requests/{self.request_a_dos.id}/"
        )

        self.assertEqual(response.status_code, 404)

    def test_events_coordinator_only_sees_event_area_requests(self):
        self.authenticate(self.coordinador)

        response = self.client.get("/api/services/requests/")

        self.assertEqual(response.status_code, 200)

        ids = [item["id"] for item in response.data["results"]]

        self.assertIn(self.request_event.id, ids)
        self.assertNotIn(self.request_a.id, ids)
        self.assertNotIn(self.request_b.id, ids)

    def test_reception_can_create_request(self):
        self.authenticate(self.recepcion)

        response = self.client.post(
            "/api/services/requests/",
            {
                "service_type": self.service_type_a.id,
                "guest_name": "Huésped nuevo",
                "room_number": "501",
                "description": "Solicitud creada en prueba.",
                "priority": "HIGH",
                "channel": "RECEPTION",
                "assigned_area": self.area_a.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        created = ServiceRequest.objects.get(
            id=response.data["id"]
        )

        self.assertEqual(created.hotel_id, self.hotel_a.id)
        self.assertEqual(created.status, "RECEIVED")
        self.assertTrue(created.request_code)

        self.assertTrue(
            RequestHistory.objects.filter(
                request=created,
                new_status="RECEIVED",
            ).exists()
        )

    def test_reception_cannot_create_service_type(self):
        self.authenticate(self.recepcion)

        response = self.client.post(
            "/api/services/types/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_supervisor_can_create_request_but_not_service_type(self):
        self.authenticate(self.supervisor)

        request_response = self.client.post(
            "/api/services/requests/",
            {
                "service_type": self.service_type_a.id,
                "guest_name": "Huésped supervisor",
                "description": "Solicitud del supervisor.",
                "priority": "MEDIUM",
                "channel": "INTERNAL",
                "assigned_area": self.area_a.id,
            },
            format="json",
        )

        self.assertEqual(request_response.status_code, 201)

        type_response = self.client.post(
            "/api/services/types/",
            {},
            format="json",
        )

        self.assertEqual(type_response.status_code, 403)

    def test_operational_employee_can_update_own_request(self):
        self.authenticate(self.operativo)

        response = self.client.patch(
            f"/api/services/requests/{self.request_a.id}/",
            {"status": "IN_PROGRESS"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.request_a.refresh_from_db()

        self.assertEqual(self.request_a.status, "IN_PROGRESS")
        self.assertIsNotNone(self.request_a.first_response_at)

        self.assertTrue(
            RequestHistory.objects.filter(
                request=self.request_a,
                previous_status="RECEIVED",
                new_status="IN_PROGRESS",
            ).exists()
        )

    def test_operational_employee_cannot_update_another_employee_request(self):
        self.authenticate(self.operativo)

        response = self.client.patch(
            f"/api/services/requests/{self.request_a_dos.id}/",
            {"status": "IN_PROGRESS"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_history_is_read_only(self):
        self.authenticate(self.gerente)

        history = RequestHistory.objects.get(
            request=self.request_a
        )

        response = self.client.patch(
            f"/api/services/history/{history.id}/",
            {"observations": "Intento de modificación."},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_history_is_filtered_by_hotel(self):
        self.authenticate(self.gerente)

        response = self.client.get("/api/services/history/")

        self.assertEqual(response.status_code, 200)

        request_ids = [
            item["request"]
            for item in response.data["results"]
        ]

        self.assertIn(self.request_a.id, request_ids)
        self.assertNotIn(self.request_b.id, request_ids)
