import uuid

from django.conf import settings
from django.db import models

from core.models import BaseModel
from core.validators import validate_cnpj

APPROVAL_STATUS_PENDING = 'pending'
APPROVAL_STATUS_APPROVED = 'approved'
APPROVAL_STATUS_REJECTED = 'rejected'

APPROVAL_STATUS_CHOICES = [
    (APPROVAL_STATUS_PENDING, 'Pendente'),
    (APPROVAL_STATUS_APPROVED, 'Aprovado'),
    (APPROVAL_STATUS_REJECTED, 'Rejeitado'),
]


class Studio(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=14, unique=True, validators=[validate_cnpj])
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    address_street = models.CharField(max_length=255)
    address_number = models.CharField(max_length=20)
    neighborhood = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, verbose_name='UF')
    cep = models.CharField(max_length=9)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='owned_studios',
        blank=True,
    )
    staffs = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='assigned_studios',
        blank=True,
    )

    class Meta:
        verbose_name = 'estúdio'
        verbose_name_plural = 'estúdios'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def full_address(self):
        return (
            f'{self.address_street}, {self.address_number} — '
            f'{self.neighborhood}, {self.city}/{self.state}'
        )


class StudioApprovalRequest(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    studio = models.OneToOneField(
        Studio,
        on_delete=models.CASCADE,
        related_name='approval_request',
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='studio_approval_requests',
    )
    status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default=APPROVAL_STATUS_PENDING,
    )

    class Meta:
        verbose_name = 'solicitação de aprovação'
        verbose_name_plural = 'solicitações de aprovação'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.studio.name} — {self.get_status_display()}'


class TattooArtist(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    studio = models.ForeignKey(
        Studio,
        on_delete=models.CASCADE,
        related_name='artists',
    )
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    specialties = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = 'tatuador'
        verbose_name_plural = 'tatuadores'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.studio.name})'


class PortfolioItem(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artist = models.ForeignKey(
        TattooArtist,
        on_delete=models.CASCADE,
        related_name='portfolio_items',
    )
    image = models.ImageField(upload_to='portfolios/')

    class Meta:
        verbose_name = 'item de portfólio'
        verbose_name_plural = 'itens de portfólio'
        ordering = ['-created_at']

    def __str__(self):
        return f'Portfólio de {self.artist.name}'
