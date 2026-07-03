import re
import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models, transaction

from core.constants import CLIENT, ROLE_CHOICES, SYSTEM_ADMIN
from core.validators import validate_cpf


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', SYSTEM_ADMIN)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário precisa ter is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cpf = models.CharField(max_length=11, unique=True, validators=[validate_cpf])
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    username = models.CharField(max_length=12, unique=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CLIENT)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['cpf', 'phone']

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'

    def __str__(self):
        return self.username or self.email

    def save(self, *args, **kwargs):
        if self.cpf:
            self.cpf = re.sub(r'\D', '', self.cpf)
        if not self.username:
            with transaction.atomic():
                last = (
                    CustomUser.objects.select_for_update()
                    .exclude(username='')
                    .order_by('-username')
                    .first()
                )
                n = int(last.username.replace('INK', '')) + 1 if last else 1
                self.username = f'INK{n:04d}'
        super().save(*args, **kwargs)
