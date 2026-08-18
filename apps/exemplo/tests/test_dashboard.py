"""Testes automatizados para o Dashboard Analítico e agregações ORM (EX-03 / D-30 / D-31)."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.exemplo.models import CategoriaChoices, ItemExemplo, StatusChoices

Usuario = get_user_model()


class DashboardAnaliticoTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            email="analista@cfc.org.br",
            password="SenhaForte123!@#",
            first_name="Analista Teste",
        )
        self.client.force_login(self.usuario)
        self.url_dashboard = reverse("exemplo:dashboard")

    def test_dashboard_requer_autenticacao(self):
        cliente_anonimo = Client()
        resposta = cliente_anonimo.get(self.url_dashboard)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("core:login"), resposta.url)

    def test_dashboard_calcula_kpis_com_agregacoes_orm_corretas(self):
        # 2 Operacionais Concluídos (Valor total: 3000)
        ItemExemplo.objects.create(
            titulo="Op 1",
            categoria=CategoriaChoices.OPERACIONAL,
            status=StatusChoices.CONCLUIDO,
            valor=Decimal("1000.00"),
            ativo=True,
        )
        ItemExemplo.objects.create(
            titulo="Op 2",
            categoria=CategoriaChoices.OPERACIONAL,
            status=StatusChoices.CONCLUIDO,
            valor=Decimal("2000.00"),
            ativo=True,
        )
        # 1 Estratégico Em Andamento (Valor: 3000)
        ItemExemplo.objects.create(
            titulo="Est 1",
            categoria=CategoriaChoices.ESTRATEGICO,
            status=StatusChoices.EM_ANDAMENTO,
            valor=Decimal("3000.00"),
            ativo=True,
        )
        # 1 Financeiro Cancelado (Valor: 4000)
        ItemExemplo.objects.create(
            titulo="Fin 1",
            categoria=CategoriaChoices.FINANCEIRO,
            status=StatusChoices.CANCELADO,
            valor=Decimal("4000.00"),
            ativo=True,
        )
        # 1 Inativo (não deve entrar nas agregações do dashboard)
        ItemExemplo.objects.create(
            titulo="Inativo",
            categoria=CategoriaChoices.OPERACIONAL,
            status=StatusChoices.CONCLUIDO,
            valor=Decimal("9999.00"),
            ativo=False,
        )

        resposta = self.client.get(self.url_dashboard)
        self.assertEqual(resposta.status_code, 200)

        kpis = resposta.context["kpis"]
        self.assertEqual(kpis["total_itens"], 4)
        self.assertEqual(kpis["valor_total"], Decimal("10000.00"))
        self.assertEqual(kpis["valor_medio"], Decimal("2500.00"))
        self.assertEqual(kpis["concluidos"], 2)
        self.assertEqual(kpis["taxa_conclusao"], Decimal("50.0"))

    def test_dashboard_agrupa_por_categoria_e_status(self):
        ItemExemplo.objects.create(
            titulo="A",
            categoria=CategoriaChoices.OPERACIONAL,
            status=StatusChoices.RASCUNHO,
            valor=Decimal("1500.00"),
        )
        ItemExemplo.objects.create(
            titulo="B",
            categoria=CategoriaChoices.OPERACIONAL,
            status=StatusChoices.CONCLUIDO,
            valor=Decimal("2500.00"),
        )
        ItemExemplo.objects.create(
            titulo="C",
            categoria=CategoriaChoices.ESTRATEGICO,
            status=StatusChoices.EM_ANDAMENTO,
            valor=Decimal("5000.00"),
        )

        resposta = self.client.get(self.url_dashboard)
        self.assertEqual(resposta.status_code, 200)

        dados_cat = resposta.context["dados_categoria"]
        # Maior valor em primeiro lugar (Estratégico: 5000, Operacional: 4000)
        self.assertEqual(dados_cat[0]["categoria_raw"], CategoriaChoices.ESTRATEGICO)
        self.assertEqual(dados_cat[0]["total_valor"], 5000.0)
        self.assertEqual(dados_cat[0]["qtd"], 1)

        self.assertEqual(dados_cat[1]["categoria_raw"], CategoriaChoices.OPERACIONAL)
        self.assertEqual(dados_cat[1]["total_valor"], 4000.0)
        self.assertEqual(dados_cat[1]["qtd"], 2)

        dados_stat = resposta.context["dados_status"]
        status_map = {item["status"]: item for item in dados_stat}
        self.assertEqual(status_map[StatusChoices.RASCUNHO]["qtd"], 1)
        self.assertEqual(status_map[StatusChoices.CONCLUIDO]["qtd"], 1)
        self.assertEqual(status_map[StatusChoices.EM_ANDAMENTO]["qtd"], 1)

    def test_dashboard_renderiza_json_script_e_scripts_echarts(self):
        resposta = self.client.get(self.url_dashboard)
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, '<script id="dados-categoria" type="application/json">')
        self.assertContains(resposta, '<script id="dados-status" type="application/json">')
        self.assertContains(resposta, 'src="/static/vendor/echarts.min.js"')
        self.assertContains(resposta, 'id="grafico-categoria"')
        self.assertContains(resposta, 'id="grafico-status"')

    def test_dashboard_com_banco_vazio_trata_nulos_com_seguranca(self):
        ItemExemplo.objects.all().delete()

        resposta = self.client.get(self.url_dashboard)
        self.assertEqual(resposta.status_code, 200)

        kpis = resposta.context["kpis"]
        self.assertEqual(kpis["total_itens"], 0)
        self.assertEqual(kpis["valor_total"], Decimal("0.00"))
        self.assertEqual(kpis["valor_medio"], Decimal("0.00"))
        self.assertEqual(kpis["concluidos"], 0)
        self.assertEqual(kpis["taxa_conclusao"], Decimal("0.0"))
        self.assertEqual(len(resposta.context["dados_categoria"]), 0)
        self.assertEqual(len(resposta.context["dados_status"]), 0)
