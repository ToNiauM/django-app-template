"""Testes automatizados para o CRUD de referência (listagem, filtros, ordenação, paginação e modais HTMX)."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.exemplo.models import CategoriaChoices, ItemExemplo, StatusChoices

Usuario = get_user_model()


class ItemExemploCrudTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            email="gestor@cfc.org.br",
            password="SenhaForte123!@#",
            first_name="Gestor Teste",
        )
        self.client.force_login(self.usuario)

        self.url_listar = reverse("exemplo:item_listar")
        self.url_criar = reverse("exemplo:item_criar")

    def test_listagem_requer_autenticacao(self):
        cliente_anonimo = Client()
        resposta = cliente_anonimo.get(self.url_listar)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("core:login"), resposta.url)

    def test_listagem_renderiza_shell_completo_para_requisicao_padrao(self):
        resposta = self.client.get(self.url_listar)
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "exemplo/item_listar.html")
        self.assertTemplateUsed(resposta, "exemplo/_filtros.html")
        self.assertTemplateUsed(resposta, "exemplo/_tabela_resultado.html")

    def test_listagem_retorna_fragmento_para_requisicao_htmx(self):
        resposta = self.client.get(self.url_listar, HTTP_HX_REQUEST="true")
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "exemplo/_tabela_resultado.html")
        self.assertTemplateNotUsed(resposta, "exemplo/item_listar.html")

    def test_busca_textual_filtra_por_titulo_ou_descricao(self):
        ItemExemplo.objects.create(
            titulo="Licença de Banco de Dados",
            descricao="Oracle 19c Enterprise",
            categoria=CategoriaChoices.OPERACIONAL,
            status=StatusChoices.CONCLUIDO,
            valor=Decimal("50000.00"),
        )
        ItemExemplo.objects.create(
            titulo="Consultoria Tributária",
            descricao="Revisão fiscal anual",
            categoria=CategoriaChoices.FINANCEIRO,
            status=StatusChoices.EM_ANDAMENTO,
            valor=Decimal("30000.00"),
        )

        # Busca por palavra no título
        resposta = self.client.get(self.url_listar, {"q": "Banco"}, HTTP_HX_REQUEST="true")
        self.assertContains(resposta, "Licença de Banco de Dados")
        self.assertNotContains(resposta, "Consultoria Tributária")

        # Busca por palavra na descrição
        resposta = self.client.get(self.url_listar, {"q": "fiscal"}, HTTP_HX_REQUEST="true")
        self.assertContains(resposta, "Consultoria Tributária")
        self.assertNotContains(resposta, "Licença de Banco de Dados")

    def test_filtros_multi_selecao_categoria_e_status(self):
        ItemExemplo.objects.create(
            titulo="Item Operacional",
            categoria=CategoriaChoices.OPERACIONAL,
            status=StatusChoices.RASCUNHO,
            valor=Decimal("1000.00"),
        )
        ItemExemplo.objects.create(
            titulo="Item Financeiro",
            categoria=CategoriaChoices.FINANCEIRO,
            status=StatusChoices.CONCLUIDO,
            valor=Decimal("2000.00"),
        )
        ItemExemplo.objects.create(
            titulo="Item Estratégico",
            categoria=CategoriaChoices.ESTRATEGICO,
            status=StatusChoices.EM_ANDAMENTO,
            valor=Decimal("3000.00"),
        )

        resposta = self.client.get(
            self.url_listar,
            {"categoria": [CategoriaChoices.OPERACIONAL, CategoriaChoices.FINANCEIRO]},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(resposta, "Item Operacional")
        self.assertContains(resposta, "Item Financeiro")
        self.assertNotContains(resposta, "Item Estratégico")

        resposta_status = self.client.get(
            self.url_listar,
            {"status": [StatusChoices.CONCLUIDO]},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(resposta_status, "Item Financeiro")
        self.assertNotContains(resposta_status, "Item Operacional")
        self.assertNotContains(resposta_status, "Item Estratégico")

    def test_ordenacao_segura_com_whitelist(self):
        ItemExemplo.objects.create(
            titulo="Item Barato",
            valor=Decimal("100.00"),
            categoria=CategoriaChoices.OPERACIONAL,
        )
        ItemExemplo.objects.create(
            titulo="Item Caro",
            valor=Decimal("9000.00"),
            categoria=CategoriaChoices.OPERACIONAL,
        )

        # Ordenação crescente de valor
        resp_asc = self.client.get(self.url_listar, {"ordem": "valor"}, HTTP_HX_REQUEST="true")
        conteudo_asc = resp_asc.content.decode("utf-8")
        self.assertTrue(conteudo_asc.find("Item Barato") < conteudo_asc.find("Item Caro"))

        # Ordenação decrescente de valor
        resp_desc = self.client.get(self.url_listar, {"ordem": "-valor"}, HTTP_HX_REQUEST="true")
        conteudo_desc = resp_desc.content.decode("utf-8")
        self.assertTrue(conteudo_desc.find("Item Caro") < conteudo_desc.find("Item Barato"))

        # Parâmetro não permitido (fallback seguro para -criado_em sem erro 500)
        resp_fallback = self.client.get(self.url_listar, {"ordem": "campo_invalido;DROP TABLE;"}, HTTP_HX_REQUEST="true")
        self.assertEqual(resp_fallback.status_code, 200)

    def test_paginacao_preserva_filtros(self):
        for i in range(15):
            ItemExemplo.objects.create(
                titulo=f"Item Teste {i:02d}",
                categoria=CategoriaChoices.OPERACIONAL,
                valor=Decimal("100.00"),
            )

        resposta_p1 = self.client.get(self.url_listar, {"categoria": CategoriaChoices.OPERACIONAL, "pagina": 1})
        self.assertEqual(resposta_p1.status_code, 200)
        self.assertEqual(resposta_p1.context["pagina"].number, 1)
        self.assertEqual(resposta_p1.context["pagina"].paginator.count, 15)
        self.assertEqual(len(resposta_p1.context["pagina"].object_list), 10)

        resposta_p2 = self.client.get(self.url_listar, {"categoria": CategoriaChoices.OPERACIONAL, "pagina": 2})
        self.assertEqual(resposta_p2.status_code, 200)
        self.assertEqual(resposta_p2.context["pagina"].number, 2)
        self.assertEqual(len(resposta_p2.context["pagina"].object_list), 5)
        self.assertIn("categoria=OPERACIONAL", resposta_p2.context["querystring_filtros"])

    def test_criar_item_valido_via_htmx(self):
        dados = {
            "titulo": "Novo Processo Licitatório",
            "descricao": "Edital 2026/01",
            "categoria": CategoriaChoices.ESTRATEGICO,
            "status": StatusChoices.EM_ANDAMENTO,
            "valor": "12500.50",
            "prazo": "2026-12-31",
        }
        resposta = self.client.post(self.url_criar, dados, HTTP_HX_REQUEST="true")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.headers.get("HX-Trigger"), "itemSalvo")

        item = ItemExemplo.objects.filter(titulo="Novo Processo Licitatório").first()
        self.assertIsNotNone(item)
        self.assertEqual(item.valor, Decimal("12500.50"))
        self.assertEqual(item.criado_por, self.usuario)
        self.assertEqual(item.history.count(), 1)

    def test_criar_item_invalido_retorna_http_422(self):
        dados_invalidos = {
            "titulo": "",  # obrigatório
            "categoria": CategoriaChoices.OPERACIONAL,
            "status": StatusChoices.RASCUNHO,
            "valor": "-500.00",  # negativo inválido
        }
        resposta = self.client.post(self.url_criar, dados_invalidos, HTTP_HX_REQUEST="true")
        self.assertEqual(resposta.status_code, 422)
        self.assertTemplateUsed(resposta, "exemplo/_form_modal.html")
        self.assertContains(resposta, "Este campo é obrigatório", status_code=422)
        self.assertContains(resposta, "O valor não pode ser negativo", status_code=422)

    def test_editar_item_via_htmx(self):
        item = ItemExemplo.objects.create(
            titulo="Item Antigo",
            categoria=CategoriaChoices.OPERACIONAL,
            status=StatusChoices.RASCUNHO,
            valor=Decimal("1000.00"),
        )
        url_editar = reverse("exemplo:item_editar", kwargs={"pk": item.pk})

        dados_editados = {
            "titulo": "Item Atualizado",
            "descricao": "Descrição editada",
            "categoria": CategoriaChoices.FINANCEIRO,
            "status": StatusChoices.CONCLUIDO,
            "valor": "2500.00",
        }
        resposta = self.client.post(url_editar, dados_editados, HTTP_HX_REQUEST="true")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.headers.get("HX-Trigger"), "itemSalvo")

        item.refresh_from_db()
        self.assertEqual(item.titulo, "Item Atualizado")
        self.assertEqual(item.status, StatusChoices.CONCLUIDO)
        self.assertEqual(item.valor, Decimal("2500.00"))

    def test_excluir_item_via_htmx(self):
        item = ItemExemplo.objects.create(
            titulo="Item a Deletar",
            categoria=CategoriaChoices.ADMINISTRATIVO,
            valor=Decimal("50.00"),
        )
        url_excluir = reverse("exemplo:item_excluir", kwargs={"pk": item.pk})

        # GET renderiza o modal de confirmação
        resp_get = self.client.get(url_excluir, HTTP_HX_REQUEST="true")
        self.assertEqual(resp_get.status_code, 200)
        self.assertTemplateUsed(resp_get, "exemplo/_confirmar_exclusao_modal.html")
        self.assertContains(resp_get, "Item a Deletar")

        # POST efetua a exclusão
        resp_post = self.client.post(url_excluir, HTTP_HX_REQUEST="true")
        self.assertEqual(resp_post.status_code, 200)
        self.assertEqual(resp_post.headers.get("HX-Trigger"), "itemSalvo")
        self.assertFalse(ItemExemplo.objects.filter(pk=item.pk).exists())
