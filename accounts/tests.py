from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import connections
from django.test import TestCase, TransactionTestCase

from accounts.models import CustomUser
from core.constants import CLIENT, STUDIO_OWNER
from core.validators import validate_cpf


class CustomUserTests(TestCase):
    def test_invalid_cpf_rejected(self):
        with self.assertRaises(ValidationError):
            validate_cpf('11111111111')

    def test_sequential_username_generation(self):
        user1 = CustomUser.objects.create_user(
            email='a@example.com',
            password='testpass123',
            cpf='52998224725',
            phone='11999999999',
            role=CLIENT,
        )
        user2 = CustomUser.objects.create_user(
            email='b@example.com',
            password='testpass123',
            cpf='39053344705',
            phone='11988888888',
            role=CLIENT,
        )
        self.assertEqual(user1.username, 'INK0001')
        self.assertEqual(user2.username, 'INK0002')

    def test_role_syncs_to_group(self):
        user = CustomUser.objects.create_user(
            email='owner@example.com',
            password='testpass123',
            cpf='15350946056',
            phone='11977777777',
            role=STUDIO_OWNER,
        )
        self.assertTrue(
            user.groups.filter(name='STUDIO_OWNER').exists()
        )


class CustomUserConcurrencyTests(TransactionTestCase):
    def test_parallel_username_generation_is_unique(self):
        import threading

        cpfs = [
            '52998224725',
            '39053344705',
            '15350946056',
            '11144477735',
            '12345678909',
        ]
        usernames = []
        errors = []
        lock = threading.Lock()

        def create_user(index):
            try:
                connections.close_all()
                user = CustomUser.objects.create_user(
                    email=f'user{index}@example.com',
                    password='testpass123',
                    cpf=cpfs[index],
                    phone=f'1199999{index:04d}',
                    role=CLIENT,
                )
                with lock:
                    usernames.append(user.username)
            except Exception as exc:
                with lock:
                    errors.append(exc)

        threads = [
            threading.Thread(target=create_user, args=(i,))
            for i in range(len(cpfs))
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(errors, [])
        self.assertEqual(len(usernames), len(set(usernames)))
        self.assertEqual(len(usernames), len(cpfs))
