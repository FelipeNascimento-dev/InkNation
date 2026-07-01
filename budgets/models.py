import uuid

from django.conf import settings
from django.db import models

from studios.models import Studio, TattooArtist

STATUS_CHOICES = [
    ('sent', 'Enviado'),
    ('in_review', 'Em análise'),
    ('quoted', 'Orçado'),
    ('accepted', 'Aceito'),
    ('rejected', 'Rejeitado'),
    ('cancelled', 'Cancelado'),
]


class BudgetRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budget_requests',
    )
    studio = models.ForeignKey(
        Studio,
        on_delete=models.CASCADE,
        related_name='budget_requests',
    )
    artist = models.ForeignKey(
        TattooArtist,
        on_delete=models.CASCADE,
        related_name='budget_requests',
    )
    description = models.TextField()
    reference_image = models.ImageField(
        upload_to='budgets/%Y/%m/',
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='sent',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'solicitação de orçamento'
        verbose_name_plural = 'solicitações de orçamento'
        ordering = ['-created_at']

    def __str__(self):
        return f'Orçamento {self.client} → {self.studio.name}'
