"""Testes automatizados para o Dashboard de viagens: agregações ORM, json_script e paleta da marca."""

import json
import re
from datetime import date
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.diarias.models import StatusChoices, Viagem

Usuario = get_user_model()


def criar_viagem(**campos):
    """Fábrica mínima de Viagem válida — os testes sobrescrevem só o que importa."""
    dados = {
        "servidor": "Servidor Padrão",
        "destino": "Brasília/DF",
        "data_inicio": date(2026, 3, 10),
        "data_fim": date(2026, 3, 12),
        "motivo": "Motivo padrão de teste.",
        "valor_diarias": Decimal("100.00"),
        "valor_passagens": Decimal("200.00"),
        "status": StatusChoices.SOLICITADA,
    }
    dados.update(campos)
    return Viagem.objects.create(**dados)


class DashboardViagensTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            email="analista@diarias.test",
            password="SenhaForte123!@#",
            first_name="Analista Teste",
        )
        self.client.force_login(self.usuario)
        self.url_dashboard = reverse("diarias:dashboard")

    def test_dashboard_requer_autenticacao(self):
        cliente_anonimo = Client()
        resposta = cliente_anonimo.get(self.url_dashboard)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("core:login"), resposta.url)

    def test_dashboard_calcula_kpis_com_agregacoes_orm_corretas(self):
        # 2 pagas (diárias 1000 + 2000; passagens 500 + 500)
        criar_viagem(status=StatusChoices.PAGA, valor_diarias=Decimal("1000.00"), valor_passagens=Decimal("500.00"))
        criar_viagem(status=StatusChoices.PAGA, valor_diarias=Decimal("2000.00"), valor_passagens=Decimal("500.00"))
        # 1 aprovada (diárias 3000; passagens 1000)
        criar_viagem(status=StatusChoices.APROVADA, valor_diarias=Decimal("3000.00"), valor_passagens=Decimal("1000.00"))
        # 1 cancelada (diárias 4000; passagens 2000)
        criar_viagem(status=StatusChoices.CANCELADA, valor_diarias=Decimal("4000.00"), valor_passagens=Decimal("2000.00"))

        resposta = self.client.get(self.url_dashboard)
        self.assertEqual(resposta.status_code, 200)

        kpis = resposta.context["kpis"]
        self.assertEqual(kpis["total_viagens"], 4)
        self.assertEqual(kpis["total_diarias"], Decimal("10000.00"))
        self.assertEqual(kpis["total_passagens"], Decimal("4000.00"))
        self.assertEqual(kpis["valor_total"], Decimal("14000.00"))
        self.assertEqual(kpis["pagas"], 2)
        self.assertEqual(kpis["taxa_pagamento"], Decimal("50.0"))

    def test_dashboard_agrupa_por_status(self):
        criar_viagem(status=StatusChoices.SOLICITADA, valor_diarias=Decimal("1000.00"), valor_passagens=Decimal("500.00"))
        criar_viagem(status=StatusChoices.SOLICITADA, valor_diarias=Decimal("2000.00"), valor_passagens=Decimal("500.00"))
        criar_viagem(status=StatusChoices.PAGA, valor_diarias=Decimal("3000.00"), valor_passagens=Decimal("1000.00"))

        resposta = self.client.get(self.url_dashboard)
        self.assertEqual(resposta.status_code, 200)

        dados_stat = resposta.context["dados_status"]
        status_map = {item["status"]: item for item in dados_stat}

        self.assertEqual(status_map[StatusChoices.SOLICITADA]["qtd"], 2)
        self.assertEqual(status_map[StatusChoices.SOLICITADA]["total_valor"], 4000.0)
        self.assertEqual(status_map[StatusChoices.SOLICITADA]["rotulo"], "Solicitada")

        self.assertEqual(status_map[StatusChoices.PAGA]["qtd"], 1)
        self.assertEqual(status_map[StatusChoices.PAGA]["total_valor"], 4000.0)
        self.assertEqual(status_map[StatusChoices.PAGA]["rotulo"], "Paga")

    def test_dashboard_agrega_serie_mensal_por_mes_de_inicio(self):
        # Janeiro/2026: duas viagens
        criar_viagem(
            data_inicio=date(2026, 1, 10),
            data_fim=date(2026, 1, 12),
            valor_diarias=Decimal("1000.00"),
            valor_passagens=Decimal("300.00"),
        )
        criar_viagem(
            data_inicio=date(2026, 1, 20),
            data_fim=date(2026, 1, 22),
            valor_diarias=Decimal("500.00"),
            valor_passagens=Decimal("200.00"),
        )
        # Fevereiro/2026: uma viagem
        criar_viagem(
            data_inicio=date(2026, 2, 5),
            data_fim=date(2026, 2, 7),
            valor_diarias=Decimal("2000.00"),
            valor_passagens=Decimal("700.00"),
        )

        resposta = self.client.get(self.url_dashboard)
        self.assertEqual(resposta.status_code, 200)

        dados_mensais = resposta.context["dados_mensais"]
        self.assertEqual(len(dados_mensais), 2)

        # Ordenados por mês crescente
        janeiro, fevereiro = dados_mensais
        self.assertEqual(janeiro["mes"], "2026-01-01")
        self.assertEqual(janeiro["qtd"], 2)
        self.assertEqual(janeiro["total_diarias"], 1500.0)
        self.assertEqual(janeiro["total_passagens"], 500.0)

        self.assertEqual(fevereiro["mes"], "2026-02-01")
        self.assertEqual(fevereiro["qtd"], 1)
        self.assertEqual(fevereiro["total_diarias"], 2000.0)
        self.assertEqual(fevereiro["total_passagens"], 700.0)

    def test_dashboard_renderiza_json_script_e_scripts_echarts(self):
        resposta = self.client.get(self.url_dashboard)
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, '<script id="dados-mensais" type="application/json">')
        self.assertContains(resposta, '<script id="dados-status" type="application/json">')
        self.assertContains(resposta, 'src="/static/vendor/echarts.min.js"')
        self.assertContains(resposta, 'id="grafico-mensal"')
        self.assertContains(resposta, 'id="grafico-status"')

    def test_dashboard_com_banco_vazio_trata_nulos_com_seguranca(self):
        Viagem.objects.all().delete()

        resposta = self.client.get(self.url_dashboard)
        self.assertEqual(resposta.status_code, 200)

        kpis = resposta.context["kpis"]
        self.assertEqual(kpis["total_viagens"], 0)
        self.assertEqual(kpis["total_diarias"], Decimal("0.00"))
        self.assertEqual(kpis["total_passagens"], Decimal("0.00"))
        self.assertEqual(kpis["valor_total"], Decimal("0.00"))
        self.assertEqual(kpis["pagas"], 0)
        self.assertEqual(kpis["taxa_pagamento"], Decimal("0.0"))
        self.assertEqual(len(resposta.context["dados_mensais"]), 0)
        self.assertEqual(len(resposta.context["dados_status"]), 0)

    def test_dashboard_contexto_tem_paleta_graficos(self):
        resposta = self.client.get(self.url_dashboard)
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("paleta_graficos", resposta.context)

    def test_paleta_graficos_rampa_status_tem_claro_e_escuro_com_4_cores_hex(self):
        resposta = self.client.get(self.url_dashboard)
        rampa = resposta.context["paleta_graficos"]["rampa_status"]

        self.assertIn("claro", rampa)
        self.assertIn("escuro", rampa)
        self.assertEqual(len(rampa["claro"]), 4)
        self.assertEqual(len(rampa["escuro"]), 4)
        for cor in [*rampa["claro"], *rampa["escuro"]]:
            self.assertRegex(cor, r"^#[0-9a-fA-F]{6}$")

    def test_paleta_graficos_a_marca_e_um_degrau_da_propria_rampa_clara(self):
        """A rampa é derivada da marca e a contém (D-84) — pertinência, sem índice mágico."""
        resposta = self.client.get(self.url_dashboard)
        rampa = resposta.context["paleta_graficos"]["rampa_status"]
        self.assertIn(
            settings.COR_PRIMARIA,
            rampa["claro"],
            msg=(
                f"a rampa clara {rampa['claro']} deixou de conter a própria "
                f"COR_PRIMARIA ({settings.COR_PRIMARIA}) — ela não é mais uma "
                "rampa DA marca"
            ),
        )

    def test_paleta_graficos_listas_claro_e_escuro_sao_diferentes(self):
        resposta = self.client.get(self.url_dashboard)
        rampa = resposta.context["paleta_graficos"]["rampa_status"]
        self.assertNotEqual(rampa["claro"], rampa["escuro"])

    def test_paleta_graficos_chega_ao_html_por_json_script_valido(self):
        resposta = self.client.get(self.url_dashboard)
        self.assertContains(resposta, '<script id="paleta-graficos" type="application/json">')

        html = resposta.content.decode()
        match = re.search(
            r'<script id="paleta-graficos" type="application/json">(.*?)</script>',
            html,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        paleta = json.loads(match.group(1))
        self.assertIn("rampa_status", paleta)

    def test_views_py_nao_tem_hex_literal(self):
        caminho_views = Path(__file__).resolve().parent.parent / "views.py"
        conteudo = caminho_views.read_text(encoding="utf-8")
        self.assertNotRegex(conteudo, r"#[0-9a-fA-F]{6}")
