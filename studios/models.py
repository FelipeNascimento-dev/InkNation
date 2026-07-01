import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from core.validators import validate_cnpj


class Studio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=14, unique=True, validators=[validate_cnpj])
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=9)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_active = models.BooleanField(default=False)
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='owned_studios',
        blank=True,
    )
    staffs = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='staff_studios',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'estúdio'
        verbose_name_plural = 'estúdios'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        base_slug = slugify(self.name) or 'studio'
        slug = base_slug
        counter = 1
        while Studio.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1
        return slug


APPROVAL_STATUS_CHOICES = [
    ('pending', 'Pendente'),
    ('approved', 'Aprovado'),
    ('rejected', 'Rejeitado'),
]


class StudioApprovalRequest(models.Model):
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
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'solicitação de aprovação'
        verbose_name_plural = 'solicitações de aprovação'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.studio.name} — {self.get_status_display()}'


class TattooArtist(models.Model):
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
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'tatuador'
        verbose_name_plural = 'tatuadores'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.studio.name})'


class PortfolioItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artist = models.ForeignKey(
        TattooArtist,
        on_delete=models.CASCADE,
        related_name='portfolio_items',
    )
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='portfolios/%Y/%m/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'item de portfólio'
        verbose_name_plural = 'itens de portfólio'
        ordering = ['-created_at']

    def __str__(self):
        return self.title or f'Portfólio de {self.artist.name}'
