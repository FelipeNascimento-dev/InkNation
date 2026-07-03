from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import CustomUser
from core.constants import CLIENT, STUDIO_OWNER, STUDIO_STAFF, SYSTEM_ADMIN
from core.utils.studio_access import (
    user_can_manage_studio,
    user_can_request_budget,
    user_can_view_studio,
)
from core.validators import validate_cnpj, validate_cpf
from django.core.exceptions import ValidationError
from studios.models import Studio


class CPFValidatorTests(TestCase):
    def test_valid_cpf(self):
        validate_cpf('52998224725')

    def test_invalid_cpf_length(self):
        with self.assertRaises(ValidationError):
            validate_cpf('123')

    def test_invalid_cpf_repeated_digits(self):
        with self.assertRaises(ValidationError):
            validate_cpf('11111111111')

    def test_valid_cpf_with_mask(self):
        validate_cpf('529.982.247-25')


class CNPJValidatorTests(TestCase):
    def test_valid_cnpj(self):
        validate_cnpj('11222333000181')

    def test_invalid_cnpj_length(self):
        with self.assertRaises(ValidationError):
            validate_cnpj('123')

    def test_invalid_cnpj_repeated_digits(self):
        with self.assertRaises(ValidationError):
            validate_cnpj('11111111111111')

    def test_valid_cnpj_with_mask(self):
        validate_cnpj('11.222.333/0001-81')


class HomeSmokeTests(TestCase):
    def setUp(self):
        self.client = Client()
        owner = CustomUser.objects.create_user(
            email='owner@example.com',
            password='testpass123',
            cpf='28625587887',
            phone='11977777777',
            role=STUDIO_OWNER,
        )
        studio = Studio.objects.create(
            name='Map Studio',
            cnpj='11444777000161',
            address_street='Rua E',
            address_number='20',
            neighborhood='Centro',
            city='Rio de Janeiro',
            state='RJ',
            cep='22041080',
            latitude=-22.9068,
            longitude=-43.1729,
            is_active=True,
        )
        studio.owners.add(owner)

    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Map Studio')
        self.assertContains(response, 'Estúdios em destaque')
        self.assertContains(response, 'que combina com você')


class StudioAccessTests(TestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            email='owner-access@example.com',
            password='testpass123',
            cpf='15350946056',
            phone='11977777777',
            role=STUDIO_OWNER,
        )
        self.staff = CustomUser.objects.create_user(
            email='staff-access@example.com',
            password='testpass123',
            cpf='11144477735',
            phone='11966666666',
            role=STUDIO_STAFF,
        )
        self.client_user = CustomUser.objects.create_user(
            email='client-access@example.com',
            password='testpass123',
            cpf='12345678909',
            phone='11955555555',
            role=CLIENT,
        )
        self.inactive_studio = Studio.objects.create(
            name='Pending Studio',
            cnpj='27865757000102',
            address_street='Rua A',
            address_number='1',
            neighborhood='Centro',
            city='São Paulo',
            state='SP',
            cep='01001000',
            is_active=False,
        )
        self.inactive_studio.owners.add(self.owner)
        self.inactive_studio.staffs.add(self.staff)

    def test_owner_can_view_inactive_studio(self):
        self.assertTrue(user_can_view_studio(self.owner, self.inactive_studio))

    def test_client_cannot_view_inactive_studio(self):
        self.assertFalse(user_can_view_studio(self.client_user, self.inactive_studio))

    def test_staff_can_manage_studio(self):
        self.assertTrue(user_can_manage_studio(self.staff, self.inactive_studio))

    def test_client_cannot_request_budget_on_inactive_studio(self):
        self.assertFalse(user_can_request_budget(self.client_user, self.inactive_studio))


class SuperuserRoleTests(TestCase):
    def test_create_superuser_sets_system_admin_role(self):
        admin = CustomUser.objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
            cpf='52998224725',
            phone='11999999999',
        )
        self.assertEqual(admin.role, SYSTEM_ADMIN)
