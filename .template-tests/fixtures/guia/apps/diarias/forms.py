"""Formulários do app de diárias com validações e estilos Tailwind."""

from decimal import Decimal
from django import forms

from .models import Viagem


class ViagemForm(forms.ModelForm):
    class Meta:
        model = Viagem
        fields = [
            "servidor",
            "destino",
            "data_inicio",
            "data_fim",
            "motivo",
            "valor_diarias",
            "valor_passagens",
            "status",
        ]
        widgets = {
            "servidor": forms.TextInput(
                attrs={
                    "class": "w-full rounded-sm border border-grid bg-surface px-3 py-2 text-sm text-ink placeholder:text-muted focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand",
                    "placeholder": "Ex.: Maria da Silva Costa",
                }
            ),
            "destino": forms.TextInput(
                attrs={
                    "class": "w-full rounded-sm border border-grid bg-surface px-3 py-2 text-sm text-ink placeholder:text-muted focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand",
                    "placeholder": "Ex.: Brasília/DF",
                }
            ),
            "data_inicio": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full rounded-sm border border-grid bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand",
                }
            ),
            "data_fim": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full rounded-sm border border-grid bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand",
                }
            ),
            "motivo": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "w-full rounded-sm border border-grid bg-surface px-3 py-2 text-sm text-ink placeholder:text-muted focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand",
                    "placeholder": "Descreva o motivo da viagem...",
                }
            ),
            "valor_diarias": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "class": "w-full rounded-sm border border-grid bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand font-mono",
                }
            ),
            "valor_passagens": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "class": "w-full rounded-sm border border-grid bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand font-mono",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "w-full rounded-sm border border-grid bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand"
                }
            ),
        }

    def clean_valor_diarias(self):
        valor = self.cleaned_data.get("valor_diarias")
        if valor is not None and valor < Decimal("0.00"):
            raise forms.ValidationError("O valor de diárias não pode ser negativo.")
        return valor

    def clean_valor_passagens(self):
        valor = self.cleaned_data.get("valor_passagens")
        if valor is not None and valor < Decimal("0.00"):
            raise forms.ValidationError("O valor de passagens não pode ser negativo.")
        return valor
