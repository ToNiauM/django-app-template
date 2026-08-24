"""Testes automatizados para o Dashboard Analítico e agregações ORM (EX-03 / D-30 / D-31)."""

import json
import re
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.exemplo.models import CategoriaChoices, ItemExemplo, StatusChoices
from core.tema import familia_marca
from core.tests.contraste import contraste, tokens_do_input_css

Usuario = get_user_model()


class DashboardAnaliticoTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            email="analista@exemplo.test",
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
        # 1 recurso cancelado (valor: 4000)
        ItemExemplo.objects.create(
            titulo="Fin 1",
            categoria=CategoriaChoices.RECURSOS,
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
        """A marca continua sendo um degrau da rampa (D-84) — sem índice mágico.

        A asserção antiga comparava o degrau de índice ZERO da rampa clara com
        `settings.COR_PRIMARIA` (a forma literal não é reproduzida aqui de
        propósito: o gate da fase procura por ela no fonte e uma citação em
        comentário reprovaria o arquivo que a eliminou).
        Ela deixou de valer quando a rampa ganhou um quarto degrau MAIS forte
        que a marca (G-03), e trocar o `0` por `1` seria só mover o índice
        mágico de lugar: qualquer reordenação futura voltaria a quebrá-la sem
        que nada de errado tivesse acontecido. A propriedade real é
        PERTINÊNCIA — a rampa é derivada da marca e a contém — e essa
        sobrevive a reordenação. A ORDEM é asserida à parte, e por contraste
        medido, em `PaletaDeDadoDoDonutTests`.
        """
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


class PaletaDeDadoDoDonutTests(TestCase):
    """Gate de VISIBILIDADE das quatro fatias do donut (G-03).

    Por que ele existe: a fase 07 verificou que a rampa tinha quatro cores hex
    e que elas chegavam ao HTML por `json_script` — estrutura declarada. Só que
    a quarta cor era `brand-tint`, um token de FUNDO ("fundo tênue do item
    ativo", `core/tema.py`), usado como cor de DADO. Contra o fundo do card ela
    media **1,11:1** no tema claro e **1,00:1** no escuro — no escuro,
    literalmente o mesmo tom do card. O donut tem quatro categorias de
    `StatusChoices` e desenhava três fatias visíveis: o gráfico mentia sobre a
    distribuição, e nenhuma asserção de "existe hex" pega isso.

    A prova aqui é de CONTRASTE COMPUTADO contra o fundo real do card, nos dois
    temas — a mesma classe de prova do gate de cromo (`test_grafico_chrome.py`)
    e do gate da marca (`core/tests/test_contraste_marca.py`), com a fórmula
    vindo da fonte única de `core/tests/contraste.py`.

    ## O gate tem três partes, e nenhuma delas sozinha fecha o gap

    1. **Nenhuma fatia é token de superfície.** É a parte que `brand-tint` não
       tem como satisfazer, e é o núcleo do conserto: cor de dado se deriva,
       não se pega emprestada da paleta de fundo.
    2. **Piso absoluto de 1,5:1** de cada fatia contra o fundo do card. Ele é
       deliberadamente BAIXO — mais baixo que o 3:1 do WCAG para objeto gráfico
       portador de informação — e o motivo tem dono: os três degraus herdados
       (`seq-600`/`seq-450`/`seq-300`) reproduzem byte a byte a rampa
       sequencial do padrão de referência, e o mais fraco deles vive em torno
       de 1,9:1 no claro. Exigir 3:1 aqui obrigaria a mexer nos coeficientes de
       `core/tema.py` — ou seja, a jogar fora a equivalência numérica com o
       padrão que `core/tests/test_tema.py` protege — para consertar um defeito
       que não está neles. 1,5:1 pega o 1,11/1,00 do defeito com folga larga e
       passa nos herdados sem tocá-los.
    3. **Ordenação por contraste decrescente, medida.** É o que faz a rampa
       LER como rampa sequencial em vez de como sorteio, e é uma propriedade
       relativa: auto-calibra para qualquer `COR_PRIMARIA` e nunca pede que um
       coeficiente herdado mude.

    Quem baixar o piso da parte 2 numa falha futura, ou afrouxar a parte 1 para
    deixar passar "só um" token de fundo, está apagando o G-03, não consertando
    o teste.

    ## O ponto sutil do `brand-tint`

    `tokens_do_input_css()` lê o DEFAULT do template (derivado de `#1e40af`).
    Os tokens de superfície (`page`, `surface`, `surface-2`, `surface-3`) são
    NEUTROS — não saem de `COR_PRIMARIA` — então compará-los com a rampa é
    válido em qualquer ambiente. Já `brand-tint` DEPENDE da marca: num sistema
    gerado com outra `COR_PRIMARIA`, o `brand-tint` do arquivo e o da rampa
    seriam valores diferentes, e a comparação passaria por engano — o defeito
    original sobreviveria ao seu próprio gate. Por isso o `brand-tint` proibido
    é sempre recalculado de `settings.COR_PRIMARIA`, nunca lido do CSS.
    """

    # Os cards de gráfico do dashboard são `bg-surface … dark:bg-surface-2` —
    # o fundo contra o qual a fatia é de fato pintada muda com o tema. Mesmo
    # mapeamento de `test_grafico_chrome.py`; se o HTML dos cards mudar, é lá
    # que a divergência é detectada.
    CARD_POR_TEMA = {"claro": "surface", "escuro": "surface-2"}

    # Tokens de SUPERFÍCIE neutros: nenhuma cor de dado pode ser igual a um
    # deles. `brand-tint` entra nesta lista em runtime, derivado da marca.
    SUPERFICIES_NEUTRAS = ("page", "surface", "surface-2", "surface-3")

    # Piso de visibilidade da fatia contra o fundo do card. Ver a justificativa
    # no docstring da classe antes de mexer neste número.
    PISO_DE_FATIA = 1.5

    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            email="paleta@exemplo.test",
            password="SenhaForte123!@#",
            first_name="Paleta Teste",
        )
        self.client.force_login(self.usuario)

        resposta = self.client.get(reverse("exemplo:dashboard"))
        self.assertEqual(resposta.status_code, 200)
        # A rampa vem do CONTEXTO da view — é o valor que de fato chega ao
        # `json_script` e ao ECharts, não uma reconstrução paralela que poderia
        # divergir do que a página pinta.
        self.rampa = resposta.context["paleta_graficos"]["rampa_status"]

        claro, escuro = tokens_do_input_css()
        self.tokens = {"claro": claro, "escuro": escuro}

        familia = familia_marca(settings.COR_PRIMARIA)
        self.brand_tint = {
            "claro": familia["brand-tint"],
            "escuro": familia["brand-tint:escuro"],
        }

    def _card(self, tema_nome):
        return self.tokens[tema_nome][self.CARD_POR_TEMA[tema_nome]]

    def _proibidos(self, tema_nome):
        """Tokens que uma cor de DADO nunca pode ser, no tema dado."""
        proibidos = {
            nome: self.tokens[tema_nome][nome] for nome in self.SUPERFICIES_NEUTRAS
        }
        proibidos["brand-tint"] = self.brand_tint[tema_nome]
        return proibidos

    def test_nenhuma_fatia_e_token_de_superficie(self):
        """Parte 1 do gate — a que `brand-tint` não consegue satisfazer."""
        for tema_nome in ("claro", "escuro"):
            proibidos = self._proibidos(tema_nome)
            for indice, cor in enumerate(self.rampa[tema_nome]):
                with self.subTest(tema=tema_nome, indice=indice):
                    for nome_token, valor in proibidos.items():
                        self.assertNotEqual(
                            cor.lower(),
                            valor.lower(),
                            msg=(
                                f"fatia {indice} do tema {tema_nome} é {cor} — o "
                                f"MESMO valor de --cor-{nome_token}, que é token de "
                                "SUPERFÍCIE. Cor de dado se deriva da marca (rampa "
                                "seq-*), nunca se pega emprestada da paleta de fundo."
                            ),
                        )

    def test_toda_fatia_contrasta_com_o_fundo_do_card(self):
        """Parte 2 do gate — piso absoluto, medido contra o fundo real."""
        for tema_nome in ("claro", "escuro"):
            card = self._card(tema_nome)
            for indice, cor in enumerate(self.rampa[tema_nome]):
                with self.subTest(tema=tema_nome, indice=indice):
                    medido = contraste(cor, card)
                    self.assertGreaterEqual(
                        medido,
                        self.PISO_DE_FATIA,
                        msg=(
                            f"fatia {indice} do tema {tema_nome} ({cor}) contra o "
                            f"fundo do card (--cor-{self.CARD_POR_TEMA[tema_nome]} "
                            f"= {card}) mede {medido:.2f}:1, abaixo do piso de "
                            f"{self.PISO_DE_FATIA}:1 — essa fatia é invisível e o "
                            "donut mente sobre a distribuição dos dados"
                        ),
                    )

    def test_a_primeira_fatia_e_a_de_maior_contraste(self):
        """Parte 3a — relativa e auto-calibrada: nada aqui é hex cravado."""
        for tema_nome in ("claro", "escuro"):
            card = self._card(tema_nome)
            with self.subTest(tema=tema_nome):
                medidos = [contraste(cor, card) for cor in self.rampa[tema_nome]]
                self.assertGreaterEqual(
                    medidos[0],
                    max(medidos[1:]),
                    msg=(
                        f"no tema {tema_nome} a primeira fatia não é a mais "
                        f"destacada contra o card ({card}): contrastes medidos "
                        f"{[f'{m:.2f}' for m in medidos]} para {self.rampa[tema_nome]}"
                    ),
                )

    def test_a_rampa_e_monotonica_em_contraste_contra_o_card(self):
        """Parte 3b — a formulação que funciona nos DOIS temas sem inversão.

        No tema claro a rampa escurece; no escuro ela clareia. "Ordem por
        luminosidade" precisaria de um sinal diferente em cada tema. "Ordem por
        contraste contra o fundo do card" é a mesma frase nos dois: do mais
        destacado ao menos destacado — que é o que faz uma escala sequencial
        ser lida como escala.
        """
        for tema_nome in ("claro", "escuro"):
            card = self._card(tema_nome)
            cores = self.rampa[tema_nome]
            medidos = [contraste(cor, card) for cor in cores]
            for indice in range(len(medidos) - 1):
                with self.subTest(tema=tema_nome, indice=indice):
                    self.assertGreater(
                        medidos[indice],
                        medidos[indice + 1],
                        msg=(
                            f"no tema {tema_nome} a rampa não decresce em "
                            f"contraste do degrau {indice} ({cores[indice]}, "
                            f"{medidos[indice]:.2f}:1) para o {indice + 1} "
                            f"({cores[indice + 1]}, {medidos[indice + 1]:.2f}:1) "
                            "— a escala deixou de ler como escala"
                        ),
                    )

    def test_as_quatro_fatias_de_cada_tema_sao_distintas(self):
        """Duas fatias iguais é a mesma mentira do G-03 por outro caminho."""
        for tema_nome in ("claro", "escuro"):
            with self.subTest(tema=tema_nome):
                cores = [cor.lower() for cor in self.rampa[tema_nome]]
                self.assertEqual(
                    len(set(cores)),
                    len(cores),
                    msg=(
                        f"o tema {tema_nome} repete cor entre fatias: {cores} — "
                        "duas categorias de status ficariam indistinguíveis"
                    ),
                )
