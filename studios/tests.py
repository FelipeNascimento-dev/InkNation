from django.contrib import admin
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from accounts.models import CustomUser
from core.constants import CLIENT, STUDIO_OWNER, STUDIO_STAFF
from studios.admin import approve_studio
from studios.models import (
    APPROVAL_STATUS_APPROVED,
    APPROVAL_STATUS_PENDING,
    Studio,
    StudioApprovalRequest,
)


class StudioTests(TestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            email='owner@example.com',
            password='testpass123',
            cpf='15350946056',
            phone='11977777777',
            role=STUDIO_OWNER,
        )

    def test_slug_generated_on_save(self):
        studio = Studio.objects.create(
            name='Ink Studio SP',
            cnpj='11222333000181',
            address_street='Rua A',
            address_number='100',
            neighborhood='Centro',
            city='São Paulo',
            state='SP',
            cep='01001000',
        )
        self.assertEqual(studio.slug, 'ink-studio-sp')

    def test_registration_creates_pending_approval(self):
        studio = Studio.objects.create(
            name='Ink Studio RJ',
            cnpj='11444777000161',
            address_street='Rua B',
            address_number='200',
            neighborhood='Copacabana',
            city='Rio de Janeiro',
            state='RJ',
            cep='22041080',
            is_active=False,
        )
        studio.owners.add(self.owner)
        approval = StudioApprovalRequest.objects.create(
            studio=studio,
            requested_by=self.owner,
            status='pending',
        )
        self.assertFalse(studio.is_active)
        self.assertEqual(approval.status, 'pending')


class StudioAdminTests(TestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
            cpf='52998224725',
            phone='11999999999',
        )
        self.owner = CustomUser.objects.create_user(
            email='owner@example.com',
            password='testpass123',
            cpf='39053344705',
            phone='11977777777',
            role=STUDIO_OWNER,
        )
        self.studio = Studio.objects.create(
            name='Pending Studio',
            cnpj='27865757000102',
            address_street='Rua C',
            address_number='50',
            neighborhood='Centro',
            city='São Paulo',
            state='SP',
            cep='01001000',
            is_active=False,
        )
        self.studio.owners.add(self.owner)
        self.approval = StudioApprovalRequest.objects.create(
            studio=self.studio,
            requested_by=self.owner,
            status=APPROVAL_STATUS_PENDING,
        )

    def test_approve_studio_action_activates_studio(self):
        request = RequestFactory().get('/admin/')
        request.user = self.admin_user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        queryset = Studio.objects.filter(pk=self.studio.pk)
        approve_studio(admin.site._registry[Studio], request, queryset)

        self.studio.refresh_from_db()
        self.approval.refresh_from_db()
        self.assertTrue(self.studio.is_active)
        self.assertEqual(self.approval.status, APPROVAL_STATUS_APPROVED)


class StudioSmokeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = CustomUser.objects.create_user(
            email='owner@example.com',
            password='testpass123',
            cpf='15350946056',
            phone='11977777777',
            role=STUDIO_OWNER,
        )
        self.staff = CustomUser.objects.create_user(
            email='staff@example.com',
            password='testpass123',
            cpf='11144477735',
            phone='11966666666',
            role=STUDIO_STAFF,
        )
        self.client_user = CustomUser.objects.create_user(
            email='client@example.com',
            password='testpass123',
            cpf='12345678909',
            phone='11955555555',
            role=CLIENT,
        )
        self.studio = Studio.objects.create(
            name='Active Studio',
            cnpj='11222333000181',
            address_street='Rua D',
            address_number='10',
            neighborhood='Centro',
            city='São Paulo',
            state='SP',
            cep='01001000',
            latitude=-23.5505,
            longitude=-46.6333,
            is_active=True,
        )
        self.studio.owners.add(self.owner)
        self.studio.staffs.add(self.staff)

    def test_locations_api_returns_light_payload(self):
        response = self.client.get(reverse('studio-locations-api'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(
            set(data[0].keys()),
            {
                'id', 'name', 'latitude', 'longitude', 'slug',
                'city', 'state', 'artist_count', 'cover_url',
            },
        )

    def test_dashboard_forbidden_for_client(self):
        self.client.login(email='client@example.com', password='testpass123')
        response = self.client.get(
            reverse('studio-dashboard', kwargs={'slug': self.studio.slug}),
        )
        self.assertEqual(response.status_code, 403)

    def test_dashboard_accessible_for_owner(self):
        self.client.login(email='owner@example.com', password='testpass123')
        response = self.client.get(
            reverse('studio-dashboard', kwargs={'slug': self.studio.slug}),
        )
        self.assertEqual(response.status_code, 200)
