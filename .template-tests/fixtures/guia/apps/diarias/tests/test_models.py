"""Testes unitários para o modelo Viagem, auditoria HistoricalRecords e seed_diarias."""

from datetime import date

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase

from apps.diarias.models import StatusChoices, Viagem

Usuario = get_user_model()


class ViagemModelTest(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            email="autor@diarias.test",
            password="SenhaForte123!@#",
            first_name="Autor Teste",
        )

    def test_criacao_viagem_com_campos_obrigatorios(self):
        viagem = Viagem.objects.create(
            servidor="Maria da Silva Costa",
            destino="Brasília/DF",
            data_inicio=date(2026, 3, 10),
            data_fim=date(2026, 3, 12),
            motivo="Reunião plenária ordinária do Conselho.",
            valor_diarias=Decimal("1687.00"),
            valor_passagens=Decimal("1245.90"),
            status=StatusChoices.SOLICITADA,
        )
        self.assertEqual(viagem.servidor, "Maria da Silva Costa")
        self.assertEqual(viagem.destino, "Brasília/DF")
        self.assertEqual(viagem.status, StatusChoices.SOLICITADA)
        self.assertEqual(viagem.valor_diarias, Decimal("1687.00"))
        self.assertEqual(viagem.valor_passagens, Decimal("1245.90"))
        self.assertEqual(str(viagem), "Maria da Silva Costa — Brasília/DF")

    def test_full_clean_aceita_periodo_coerente(self):
        viagem = Viagem(
            servidor="Servidor Válido",
            destino="Recife/PE",
            data_inicio=date(2026, 5, 1),
            data_fim=date(2026, 5, 3),
            motivo="Auditoria de prestação de contas.",
            valor_diarias=Decimal("100.00"),
            valor_passagens=Decimal("200.00"),
        )
        viagem.full_clean()  # não deve levantar

    def test_full_clean_reprova_data_fim_anterior_ao_inicio(self):
        viagem = Viagem(
            servidor="Servidor Período Invertido",
            destino="Salvador/BA",
            data_inicio=date(2026, 5, 10),
            data_fim=date(2026, 5, 5),
            motivo="Período incoerente para teste.",
            valor_diarias=Decimal("100.00"),
            valor_passagens=Decimal("200.00"),
        )
        with self.assertRaises(ValidationError) as contexto:
            viagem.full_clean()
        self.assertIn("data_fim", contexto.exception.message_dict)

    def test_full_clean_reprova_valor_negativo(self):
        viagem = Viagem(
            servidor="Servidor Valor Negativo",
            destino="Curitiba/PR",
            data_inicio=date(2026, 6, 1),
            data_fim=date(2026, 6, 2),
            motivo="Valor negativo para teste.",
            valor_diarias=Decimal("-10.00"),
            valor_passagens=Decimal("0.00"),
        )
        with self.assertRaises(ValidationError):
            viagem.full_clean()

    def test_auditoria_historical_records_na_criacao_e_edicao(self):
        # Criação gera histórico tipo '+'
        viagem = Viagem.objects.create(
            servidor="Servidor Auditado",
            destino="Fortaleza/CE",
            data_inicio=date(2026, 4, 1),
            data_fim=date(2026, 4, 3),
            motivo="Capacitação em mediação e arbitragem.",
            valor_diarias=Decimal("2530.50"),
            valor_passagens=Decimal("1495.20"),
            status=StatusChoices.SOLICITADA,
        )
        historicos = viagem.history.all()
        self.assertEqual(historicos.count(), 1)
        self.assertEqual(historicos.first().history_type, "+")

        # Edição gera histórico tipo '~'
        viagem.status = StatusChoices.APROVADA
        viagem.valor_diarias = Decimal("2700.00")
        viagem.save()

        historicos = viagem.history.all()
        self.assertEqual(historicos.count(), 2)
        ultimo_historico = historicos.first()
        self.assertEqual(ultimo_historico.history_type, "~")
        self.assertEqual(ultimo_historico.status, StatusChoices.APROVADA)
        self.assertEqual(ultimo_historico.valor_diarias, Decimal("2700.00"))

    def test_choices_de_status_labels(self):
        self.assertEqual(StatusChoices.SOLICITADA.label, "Solicitada")
        self.assertEqual(StatusChoices.APROVADA.label, "Aprovada")
        self.assertEqual(StatusChoices.PAGA.label, "Paga")
        self.assertEqual(StatusChoices.CANCELADA.label, "Cancelada")

    def test_comando_seed_diarias_e_idempotente(self):
        """Duas execuções seguidas não duplicam registro nenhum.

        O banco de ensaio da suíte do guia é REUSADO entre execuções — se o
        seed sorteasse dados ou usasse create() cru, cada rodada inflaria a
        tabela. A prova aqui é a contrapositiva: contagem estável e > 0.
        """
        call_command("seed_diarias")
        contagem_primeira = Viagem.objects.count()
        self.assertGreater(contagem_primeira, 0)

        call_command("seed_diarias")
        contagem_segunda = Viagem.objects.count()
        self.assertEqual(contagem_primeira, contagem_segunda)
