"""Testes automatizados para o CRUD de viagens (listagem, filtros, ordenação, paginação e modais HTMX)."""

from datetime import date

from decimal import Decimal

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


class ViagemCrudTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            email="gestor@diarias.test",
            password="SenhaForte123!@#",
            first_name="Gestor Teste",
        )
        self.client.force_login(self.usuario)

        self.url_listar = reverse("diarias:viagem_listar")
        self.url_criar = reverse("diarias:viagem_criar")

    def test_todas_as_rotas_exigem_autenticacao(self):
        """Anônimo recebe 302 para o login nas 5 rotas do app (ASVS V4)."""
        viagem = criar_viagem(servidor="Servidor Protegido")
        cliente_anonimo = Client()

        urls_protegidas = [
            reverse("diarias:viagem_listar"),
            reverse("diarias:dashboard"),
            reverse("diarias:viagem_criar"),
            reverse("diarias:viagem_editar", kwargs={"pk": viagem.pk}),
            reverse("diarias:viagem_excluir", kwargs={"pk": viagem.pk}),
        ]
        for url in urls_protegidas:
            with self.subTest(url=url):
                resposta = cliente_anonimo.get(url)
                self.assertEqual(resposta.status_code, 302)
                self.assertIn(reverse("core:login"), resposta.url)

    def test_listagem_renderiza_shell_completo_para_requisicao_padrao(self):
        resposta = self.client.get(self.url_listar)
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "diarias/viagem_listar.html")
        self.assertTemplateUsed(resposta, "diarias/_filtros.html")
        self.assertTemplateUsed(resposta, "diarias/_tabela_resultado.html")
        self.assertContains(resposta, "Diárias e passagens")

    def test_listagem_retorna_fragmento_para_requisicao_htmx(self):
        resposta = self.client.get(self.url_listar, HTTP_HX_REQUEST="true")
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "diarias/_tabela_resultado.html")
        self.assertTemplateNotUsed(resposta, "diarias/viagem_listar.html")

    def test_busca_textual_filtra_por_servidor_destino_ou_motivo(self):
        criar_viagem(
            servidor="Ana Beatriz Nogueira",
            destino="Brasília/DF",
            motivo="Reunião plenária ordinária.",
        )
        criar_viagem(
            servidor="Carlos Eduardo Menezes",
            destino="São Paulo/SP",
            motivo="Fiscalização de organizações contábeis.",
        )

        # Busca por palavra no servidor
        resposta = self.client.get(self.url_listar, {"q": "Nogueira"}, HTTP_HX_REQUEST="true")
        self.assertContains(resposta, "Ana Beatriz Nogueira")
        self.assertNotContains(resposta, "Carlos Eduardo Menezes")

        # Busca por palavra no motivo
        resposta = self.client.get(self.url_listar, {"q": "Fiscalização"}, HTTP_HX_REQUEST="true")
        self.assertContains(resposta, "Carlos Eduardo Menezes")
        self.assertNotContains(resposta, "Ana Beatriz Nogueira")

    def test_filtro_multi_selecao_de_status(self):
        criar_viagem(servidor="Viagem Solicitada", status=StatusChoices.SOLICITADA)
        criar_viagem(servidor="Viagem Aprovada", status=StatusChoices.APROVADA)
        criar_viagem(servidor="Viagem Paga", status=StatusChoices.PAGA)

        resposta = self.client.get(
            self.url_listar,
            {"status": [StatusChoices.APROVADA, StatusChoices.PAGA]},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(resposta, "Viagem Aprovada")
        self.assertContains(resposta, "Viagem Paga")
        self.assertNotContains(resposta, "Viagem Solicitada")

        # Valor desconhecido de status é descartado antes da query
        resposta_invalida = self.client.get(
            self.url_listar,
            {"status": ["NAO_EXISTE"]},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(resposta_invalida.status_code, 200)
        self.assertContains(resposta_invalida, "Viagem Solicitada")

    def test_ordenacao_segura_com_whitelist(self):
        criar_viagem(servidor="Viagem Barata", valor_diarias=Decimal("100.00"))
        criar_viagem(servidor="Viagem Cara", valor_diarias=Decimal("9000.00"))

        # Ordenação crescente de valor de diárias
        resp_asc = self.client.get(self.url_listar, {"ordem": "valor_diarias"}, HTTP_HX_REQUEST="true")
        conteudo_asc = resp_asc.content.decode("utf-8")
        self.assertTrue(conteudo_asc.find("Viagem Barata") < conteudo_asc.find("Viagem Cara"))

        # Ordenação decrescente de valor de diárias
        resp_desc = self.client.get(self.url_listar, {"ordem": "-valor_diarias"}, HTTP_HX_REQUEST="true")
        conteudo_desc = resp_desc.content.decode("utf-8")
        self.assertTrue(conteudo_desc.find("Viagem Cara") < conteudo_desc.find("Viagem Barata"))

        # Parâmetro não permitido (fallback seguro para -criado_em sem erro 500)
        resp_fallback = self.client.get(
            self.url_listar, {"ordem": "campo_invalido;DROP TABLE;"}, HTTP_HX_REQUEST="true"
        )
        self.assertEqual(resp_fallback.status_code, 200)

    def test_paginacao_preserva_filtros(self):
        for i in range(15):
            criar_viagem(servidor=f"Servidor Teste {i:02d}", status=StatusChoices.APROVADA)

        resposta_p1 = self.client.get(self.url_listar, {"status": StatusChoices.APROVADA, "pagina": 1})
        self.assertEqual(resposta_p1.status_code, 200)
        self.assertEqual(resposta_p1.context["pagina"].number, 1)
        self.assertEqual(resposta_p1.context["pagina"].paginator.count, 15)
        self.assertEqual(len(resposta_p1.context["pagina"].object_list), 10)

        resposta_p2 = self.client.get(self.url_listar, {"status": StatusChoices.APROVADA, "pagina": 2})
        self.assertEqual(resposta_p2.status_code, 200)
        self.assertEqual(resposta_p2.context["pagina"].number, 2)
        self.assertEqual(len(resposta_p2.context["pagina"].object_list), 5)
        self.assertIn("status=APROVADA", resposta_p2.context["querystring_filtros"])

    def test_criar_viagem_valida_via_htmx(self):
        dados = {
            "servidor": "Fernanda Lopes Siqueira",
            "destino": "Manaus/AM",
            "data_inicio": "2026-09-01",
            "data_fim": "2026-09-05",
            "motivo": "Fiscalização itinerante em municípios do interior.",
            "valor_diarias": "4217.50",
            "valor_passagens": "2845.60",
            "status": StatusChoices.APROVADA,
        }
        resposta = self.client.post(self.url_criar, dados, HTTP_HX_REQUEST="true")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.headers.get("HX-Trigger"), "viagemSalva")

        viagem = Viagem.objects.filter(servidor="Fernanda Lopes Siqueira").first()
        self.assertIsNotNone(viagem)
        self.assertEqual(viagem.valor_diarias, Decimal("4217.50"))
        self.assertEqual(viagem.history.count(), 1)

    def test_criar_viagem_invalida_retorna_http_422(self):
        dados_invalidos = {
            "servidor": "",  # obrigatório
            "destino": "Goiânia/GO",
            "data_inicio": "2026-09-01",
            "data_fim": "2026-09-02",
            "motivo": "Dados inválidos para teste.",
            "valor_diarias": "-500.00",  # negativo inválido
            "valor_passagens": "0.00",
            "status": StatusChoices.SOLICITADA,
        }
        resposta = self.client.post(self.url_criar, dados_invalidos, HTTP_HX_REQUEST="true")
        self.assertEqual(resposta.status_code, 422)
        self.assertTemplateUsed(resposta, "diarias/_form_modal.html")
        self.assertContains(resposta, "Este campo é obrigatório", status_code=422)
        self.assertFalse(Viagem.objects.exists())

    def test_criar_viagem_com_data_fim_anterior_retorna_http_422(self):
        dados_periodo_invertido = {
            "servidor": "Tiago Almeida Rocha",
            "destino": "Goiânia/GO",
            "data_inicio": "2026-09-10",
            "data_fim": "2026-09-05",  # antes do início
            "motivo": "Período invertido para teste do clean().",
            "valor_diarias": "100.00",
            "valor_passagens": "0.00",
            "status": StatusChoices.SOLICITADA,
        }
        resposta = self.client.post(self.url_criar, dados_periodo_invertido, HTTP_HX_REQUEST="true")
        self.assertEqual(resposta.status_code, 422)
        self.assertContains(resposta, "anterior à data de início", status_code=422)
        self.assertFalse(Viagem.objects.exists())

    def test_editar_viagem_via_htmx(self):
        viagem = criar_viagem(servidor="Servidor Antigo", status=StatusChoices.SOLICITADA)
        url_editar = reverse("diarias:viagem_editar", kwargs={"pk": viagem.pk})

        dados_editados = {
            "servidor": "Servidor Atualizado",
            "destino": "Vitória/ES",
            "data_inicio": "2026-10-01",
            "data_fim": "2026-10-03",
            "motivo": "Motivo atualizado na edição.",
            "valor_diarias": "2530.50",
            "valor_passagens": "990.60",
            "status": StatusChoices.APROVADA,
        }
        resposta = self.client.post(url_editar, dados_editados, HTTP_HX_REQUEST="true")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.headers.get("HX-Trigger"), "viagemSalva")

        viagem.refresh_from_db()
        self.assertEqual(viagem.servidor, "Servidor Atualizado")
        self.assertEqual(viagem.status, StatusChoices.APROVADA)
        self.assertEqual(viagem.valor_diarias, Decimal("2530.50"))

    def test_excluir_viagem_via_htmx(self):
        viagem = criar_viagem(servidor="Servidor a Excluir", destino="Cuiabá/MT")
        url_excluir = reverse("diarias:viagem_excluir", kwargs={"pk": viagem.pk})

        # GET renderiza o modal de confirmação
        resp_get = self.client.get(url_excluir, HTTP_HX_REQUEST="true")
        self.assertEqual(resp_get.status_code, 200)
        self.assertTemplateUsed(resp_get, "diarias/_confirmar_exclusao_modal.html")
        self.assertContains(resp_get, "Servidor a Excluir")

        # POST efetua a exclusão
        resp_post = self.client.post(url_excluir, HTTP_HX_REQUEST="true")
        self.assertEqual(resp_post.status_code, 200)
        self.assertEqual(resp_post.headers.get("HX-Trigger"), "viagemSalva")
        self.assertFalse(Viagem.objects.filter(pk=viagem.pk).exists())
