from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import CustomUser
from budgets.models import BUDGET_STATUS_ANSWERED, BUDGET_STATUS_IN_ANALYSIS, BudgetRequest
from core.constants import CLIENT, STUDIO_OWNER, STUDIO_STAFF
from studios.models import Studio, TattooArtist


class BudgetWorkflowTests(TestCase):
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
            name='Budget Studio',
            cnpj='11222333000181',
            address_street='Rua D',
            address_number='10',
            neighborhood='Centro',
            city='São Paulo',
            state='SP',
            cep='01001000',
            is_active=True,
        )
        self.studio.owners.add(self.owner)
        self.studio.staffs.add(self.staff)
        self.artist = TattooArtist.objects.create(
            studio=self.studio,
            name='Ink Artist',
            specialties='Realismo',
        )
        self.budget = BudgetRequest.objects.create(
            client=self.client_user,
            studio=self.studio,
            artist=self.artist,
            description='Tatuagem no braço',
        )

    def test_staff_can_update_budget_status(self):
        self.client.login(email='staff@example.com', password='testpass123')
        response = self.client.post(
            reverse(
                'budget-status-update',
                kwargs={'slug': self.studio.slug, 'budget_id': self.budget.pk},
            ),
            {'status': BUDGET_STATUS_IN_ANALYSIS},
        )
        self.assertEqual(response.status_code, 302)
        self.budget.refresh_from_db()
        self.assertEqual(self.budget.status, BUDGET_STATUS_IN_ANALYSIS)

    def test_client_cannot_update_budget_status(self):
        self.client.login(email='client@example.com', password='testpass123')
        response = self.client.post(
            reverse(
                'budget-status-update',
                kwargs={'slug': self.studio.slug, 'budget_id': self.budget.pk},
            ),
            {'status': BUDGET_STATUS_ANSWERED},
        )
        self.assertEqual(response.status_code, 403)

    def test_owner_can_create_artist(self):
        self.client.login(email='owner@example.com', password='testpass123')
        response = self.client.post(
            reverse('artist-create', kwargs={'slug': self.studio.slug}),
            {
                'name': 'Novo Artista',
                'bio': 'Bio curta',
                'instagram': '@novo',
                'specialties': 'Fine line',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            TattooArtist.objects.filter(studio=self.studio, name='Novo Artista').exists(),
        )

    def test_staff_cannot_create_artist(self):
        self.client.login(email='staff@example.com', password='testpass123')
        response = self.client.post(
            reverse('artist-create', kwargs={'slug': self.studio.slug}),
            {'name': 'Artista Staff', 'bio': '', 'instagram': '', 'specialties': ''},
        )
        self.assertEqual(response.status_code, 403)
