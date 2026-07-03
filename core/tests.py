from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from accounts.models import CustomUser
from core.constants import STUDIO_OWNER
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
