"""Modelos de domínio do app de diárias e passagens com escolhas tipadas e auditoria."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from simple_history.models import HistoricalRecords


class StatusChoices(models.TextChoices):
    SOLICITADA = "SOLICITADA", "Solicitada"
    APROVADA = "APROVADA", "Aprovada"
    PAGA = "PAGA", "Paga"
    CANCELADA = "CANCELADA", "Cancelada"


class Viagem(models.Model):
    """Solicitação de viagem a serviço com diárias e passagens.

    Modelo único, sem entidades relacionadas: o servidor/beneficiário é
    texto simples (como numa planilha) e o status é uma escolha tipada sem
    regras de transição. A auditoria de quem alterou o quê vem do
    django-simple-history (``history_user``), sem campo próprio no modelo.
    """

    servidor = models.CharField("servidor", max_length=150)
    destino = models.CharField("destino", max_length=150)
    data_inicio = models.DateField("início")
    data_fim = models.DateField("fim")
    motivo = models.TextField("motivo")
    valor_diarias = models.DecimalField(
        "valor de diárias",
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    valor_passagens = models.DecimalField(
        "valor de passagens",
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    status = models.CharField(
        "status",
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.SOLICITADA,
    )
    criado_em = models.DateTimeField("criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("atualizado em", auto_now=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "viagem"
        verbose_name_plural = "viagens"

    def clean(self):
        """Valida a coerência do período — é este erro que o modal 422 exibe."""
        super().clean()
        if self.data_inicio and self.data_fim and self.data_fim < self.data_inicio:
            raise ValidationError(
                {"data_fim": "A data de fim não pode ser anterior à data de início."}
            )

    def __str__(self):
        return f"{self.servidor} — {self.destino}"
