"""Formulários do app exemplo com validações e estilos Tailwind."""

from decimal import Decimal
from django import forms

from .models import ItemExemplo


class ItemExemploForm(forms.ModelForm):
    class Meta:
        model = ItemExemplo
        fields = ["titulo", "descricao", "categoria", "status", "valor", "prazo"]
        widgets = {
            "titulo": forms.TextInput(
                attrs={
                    "class": "w-full rounded-sm border border-grid bg-surface px-3 py-2 text-sm text-ink placeholder:text-muted focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand",
                    "placeholder": "Ex.: Aquisição de licenças de software",
                }
            ),
            "descricao": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "w-full rounded-sm border border-grid bg-surface px-3 py-2 text-sm text-ink placeholder:text-muted focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand",
                    "placeholder": "Descreva os detalhes do item...",
                }
            ),
            "categoria": forms.Select(
                attrs={
                    "class": "w-full rounded-sm border border-grid bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand"
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "w-full rounded-sm border border-grid bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand"
                }
            ),
            "valor": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "class": "w-full rounded-sm border border-grid bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand font-mono",
                }
            ),
            "prazo": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full rounded-sm border border-grid bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand",
                }
            ),
        }

    def clean_valor(self):
        valor = self.cleaned_data.get("valor")
        if valor is not None and valor < Decimal("0.00"):
            raise forms.ValidationError("O valor não pode ser negativo.")
        return valor
