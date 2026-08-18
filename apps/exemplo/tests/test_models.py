"""Testes unitários para o modelo ItemExemplo, auditoria HistoricalRecords e seed_exemplo."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase

from apps.exemplo.models import CategoriaChoices, ItemExemplo, StatusChoices

Usuario = get_user_model()


class ItemExemploModelTest(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            email="autor@cfc.org.br",
            password="SenhaForte123!@#",
            first_name="Autor Teste",
        )

    def test_criacao_item_exemplo_com_campos_obrigatorios(self):
        item = ItemExemplo.objects.create(
            titulo="Aquisição de Servidores",
            categoria=CategoriaChoices.OPERACIONAL,
            status=StatusChoices.RASCUNHO,
            valor=Decimal("15000.00"),
            criado_por=self.usuario,
        )
        self.assertEqual(item.titulo, "Aquisição de Servidores")
        self.assertEqual(item.categoria, CategoriaChoices.OPERACIONAL)
        self.assertEqual(item.status, StatusChoices.RASCUNHO)
        self.assertEqual(item.valor, Decimal("15000.00"))
        self.assertTrue(item.ativo)
        self.assertEqual(str(item), "Aquisição de Servidores (Rascunho)")

    def test_auditoria_historical_records_na_criacao_e_edicao(self):
        # Criação gera histórico tipo '+'
        item = ItemExemplo.objects.create(
            titulo="Item Auditado",
            categoria=CategoriaChoices.ESTRATEGICO,
            status=StatusChoices.RASCUNHO,
            valor=Decimal("5000.00"),
            criado_por=self.usuario,
        )
        historicos = item.history.all()
        self.assertEqual(historicos.count(), 1)
        self.assertEqual(historicos.first().history_type, "+")

        # Edição gera histórico tipo '~'
        item.status = StatusChoices.CONCLUIDO
        item.valor = Decimal("7500.00")
        item.save()

        historicos = item.history.all()
        self.assertEqual(historicos.count(), 2)
        ultimo_historico = historicos.first()
        self.assertEqual(ultimo_historico.history_type, "~")
        self.assertEqual(ultimo_historico.status, StatusChoices.CONCLUIDO)
        self.assertEqual(ultimo_historico.valor, Decimal("7500.00"))

    def test_validacao_valor_nao_negativo(self):
        item = ItemExemplo(
            titulo="Item Valor Negativo",
            categoria=CategoriaChoices.FINANCEIRO,
            status=StatusChoices.RASCUNHO,
            valor=Decimal("-10.00"),
        )
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_choices_de_categoria_e_status_labels(self):
        self.assertEqual(CategoriaChoices.OPERACIONAL.label, "Operacional")
        self.assertEqual(CategoriaChoices.ESTRATEGICO.label, "Estratégico")
        self.assertEqual(CategoriaChoices.ADMINISTRATIVO.label, "Administrativo")
        self.assertEqual(CategoriaChoices.FINANCEIRO.label, "Financeiro")

        self.assertEqual(StatusChoices.RASCUNHO.label, "Rascunho")
        self.assertEqual(StatusChoices.EM_ANDAMENTO.label, "Em Andamento")
        self.assertEqual(StatusChoices.CONCLUIDO.label, "Concluído")
        self.assertEqual(StatusChoices.CANCELADO.label, "Cancelado")

    def test_comando_seed_exemplo(self):
        # Executa seed com quantidade 10
        call_command("seed_exemplo", limpar=True, quantidade=10)
        self.assertEqual(ItemExemplo.objects.count(), 10)

        # Re-executa com limpar e quantidade 5
        call_command("seed_exemplo", limpar=True, quantidade=5)
        self.assertEqual(ItemExemplo.objects.count(), 5)
