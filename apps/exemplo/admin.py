"""Configuração do Django Admin para o app exemplo com suporte a SimpleHistoryAdmin."""

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import ItemExemplo


@admin.register(ItemExemplo)
class ItemExemploAdmin(SimpleHistoryAdmin):
    list_display = (
        "titulo",
        "categoria",
        "status",
        "valor",
        "prazo",
        "ativo",
        "criado_por",
        "criado_em",
    )
    list_filter = ("categoria", "status", "ativo")
    search_fields = ("titulo", "descricao")
    ordering = ("-criado_em",)
