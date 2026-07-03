import uuid

from django.conf import settings
from django.db import models

from core.models import BaseModel

BUDGET_STATUS_SENT = 'sent'
BUDGET_STATUS_IN_ANALYSIS = 'in_analysis'
BUDGET_STATUS_ANSWERED = 'answered'

BUDGET_STATUS_CHOICES = [
    (BUDGET_STATUS_SENT, 'Enviado'),
    (BUDGET_STATUS_IN_ANALYSIS, 'Em análise'),
    (BUDGET_STATUS_ANSWERED, 'Respondido'),
]


class BudgetRequest(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budget_requests',
    )
    studio = models.ForeignKey(
        'studios.Studio',
        on_delete=models.CASCADE,
        related_name='budget_requests',
    )
    artist = models.ForeignKey(
        'studios.TattooArtist',
        on_delete=models.CASCADE,
        related_name='budget_requests',
    )
    description = models.TextField()
    reference_image = models.ImageField(
        upload_to='budgets/',
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=BUDGET_STATUS_CHOICES,
        default=BUDGET_STATUS_SENT,
    )

    class Meta:
        verbose_name = 'solicitação de orçamento'
        verbose_name_plural = 'solicitações de orçamento'
        ordering = ['-created_at']

    def __str__(self):
        return f'Orçamento de {self.client.username} — {self.studio.name}'
