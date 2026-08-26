"""Configuração do Django Admin para o app de diárias com suporte a SimpleHistoryAdmin."""

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Viagem


@admin.register(Viagem)
class ViagemAdmin(SimpleHistoryAdmin):
    list_display = (
        "servidor",
        "destino",
        "data_inicio",
        "data_fim",
        "status",
        "valor_diarias",
        "valor_passagens",
    )
    list_filter = ("status",)
    search_fields = ("servidor", "destino", "motivo")
    ordering = ("-criado_em",)
