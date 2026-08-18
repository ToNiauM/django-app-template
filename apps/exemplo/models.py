"""Modelos de domínio do app exemplo com escolhas tipadas e auditoria."""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from simple_history.models import HistoricalRecords


class CategoriaChoices(models.TextChoices):
    OPERACIONAL = "OPERACIONAL", "Operacional"
    ESTRATEGICO = "ESTRATEGICO", "Estratégico"
    ADMINISTRATIVO = "ADMINISTRATIVO", "Administrativo"
    FINANCEIRO = "FINANCEIRO", "Financeiro"


class StatusChoices(models.TextChoices):
    RASCUNHO = "RASCUNHO", "Rascunho"
    EM_ANDAMENTO = "EM_ANDAMENTO", "Em Andamento"
    CONCLUIDO = "CONCLUIDO", "Concluído"
    CANCELADO = "CANCELADO", "Cancelado"


class ItemExemplo(models.Model):
    """Modelo representativo de item de exemplo demonstrando campos, validações e auditoria."""

    titulo = models.CharField("título", max_length=200)
    descricao = models.TextField("descrição", blank=True)
    categoria = models.CharField(
        "categoria",
        max_length=30,
        choices=CategoriaChoices.choices,
        default=CategoriaChoices.OPERACIONAL,
    )
    status = models.CharField(
        "status",
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.RASCUNHO,
    )
    valor = models.DecimalField(
        "valor",
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    prazo = models.DateField("prazo", null=True, blank=True)
    ativo = models.BooleanField("ativo", default=True)
    criado_em = models.DateTimeField("criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("atualizado em", auto_now=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="itens_exemplo",
        verbose_name="criado por",
    )

    history = HistoricalRecords()

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "item de exemplo"
        verbose_name_plural = "itens de exemplo"

    def __str__(self):
        return f"{self.titulo} ({self.get_status_display()})"
