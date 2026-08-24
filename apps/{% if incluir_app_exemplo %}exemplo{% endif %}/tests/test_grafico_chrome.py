"""Gate do CHROME dos dois gráficos do dashboard (G-04 / WR-04), mais os dois
adjacentes que vivem nas mesmas funções (WR-13 e IN-04).

Por que este arquivo existe separado de `test_dashboard.py`: aquele prova que
a paleta de DADO chega ao HTML por `json_script` e que a agregação é ORM —
contrato de dado. Este prova que o CROMO (grade do eixo, separação entre as
fatias do donut, tooltip) lê o token do PAPEL que exerce e que o resultado é
visível. Os dois podem passar e falhar independentemente, e foi por só existir
o primeiro que o G-04 atravessou a fase: o 07-06 verificou que as seis
variáveis CSS existem nos dois temas e que o script é sintaticamente válido —
o que confirma que a LEITURA funciona, não que o VALOR lido é o certo para o
elemento em que o gráfico está montado.

O defeito, em número: os dois cards de gráfico são `bg-surface … dark:bg-surface-2`.
No escuro o card É `--cor-surface-2`; o `splitLine` lia exatamente esse token,
então a grade do eixo Y desenhava `#22211d` sobre `#22211d` — contraste
**1,00:1**, ou seja, ausência de grade. No claro o mesmo erro era discreto
(1,09:1) e por isso passou na inspeção visual.

## O piso é 1,25:1, e não 3:1 nem 4,5:1 — a justificativa

Linha de grade e separação de fatia são CROMO: não carregam dado, delimitam.
O piso de 3:1 do WCAG pertence a "objeto gráfico portador de informação" (a
barra, a fatia — responsabilidade do plano 07-13) e o de 4,5:1 pertence a
texto. Aplicar 3:1 a uma linha de grade obrigaria a grade a competir
visualmente com o dado, que é o oposto do que ela deve fazer.

O piso que de fato FECHA o gap é `> 1,00` — hoje a grade escura está
exatamente em 1,00:1. Mas um gate em `> 1,00` passaria com 1,001:1, que é
invisível do mesmo jeito. Fixamos **1,25:1** nos dois temas: é margem
suficiente para impedir uma regressão que troque um token por outro quase
idêntico (`--cor-surface-2` no claro dá 1,09:1 e reprovaria), e é folgado para
os valores reais do token de linha (≈ 1,29:1 no claro, ≈ 1,38:1 no escuro).
Este número tem dono e motivo — quem o baixar numa falha futura está apagando
o gap, não consertando o teste.

## Como a prova é possível sem navegador

Não há headless browser neste repositório e não é hora de introduzir um. A
prova tem duas metades encadeadas:

1. **Resolução no fonte.** Lê-se `dashboard.html`, extraem-se as ligações
   `const <ident> = lerVarCss("--cor-<token>");` num dicionário `ident -> token`
   e casa-se o `<ident>` usado em `splitLine.lineStyle.color`. Isso responde
   "qual variável CSS este elemento realmente usa" — exatamente o que o 07-06
   assumiu sem verificar.
2. **Contraste computado.** Com o token em mãos, o valor por tema sai de
   `tokens_do_input_css()` e a razão sai de `contraste()` — o helper WCAG único
   do repositório (`core/tests/contraste.py`, plano 07-09). Nunca hex repetido
   à mão aqui: teste e fonte que se repetem divergem em silêncio.

Todo resolvedor abaixo falha ALTO quando não acha o que procura. Um teste de
fonte que silenciosamente não casa nada e passa verde é pior do que nenhum
teste — é o modo de falha que este próprio arquivo existe para fechar.
"""

from __future__ import annotations

import re
from pathlib import Path

from django.test import SimpleTestCase

from core.tests.contraste import contraste, tokens_do_input_css

RAIZ_APP = Path(__file__).resolve().parents[1]
DASHBOARD = RAIZ_APP / "templates" / "exemplo" / "dashboard.html"

# Ver docstring: cromo, não dado nem texto.
PISO_CROMO = 1.25

# Fundo REAL do card de gráfico, por tema. Espelha as classes que os dois
# cards declaram (`bg-surface` + `dark:bg-surface-2`) — e
# `test_cards_de_grafico_declaram_a_elevacao_que_o_script_assume` amarra este
# dicionário ao HTML, para que mudar a elevação do card sem mudar o script
# acuse aqui em vez de reintroduzir o G-04 em silêncio.
CARD_POR_TEMA = {"claro": "surface", "escuro": "surface-2"}

IDS_DOS_GRAFICOS = ("grafico-categoria", "grafico-status")

LIGACAO_RE = re.compile(r'const\s+(\w+)\s*=\s*lerVarCss\(\s*"(--cor-[a-z0-9-]+)"\s*\)\s*;')
SPLITLINE_RE = re.compile(r"splitLine:\s*\{\s*lineStyle:\s*\{\s*color:\s*(\w+)\s*\}")
BORDERCOLOR_RE = re.compile(r"itemStyle:\s*\{\s*borderColor:\s*(\w+)")
CORCARD_RE = re.compile(
    r'const\s+corCard\s*=\s*temaAtual\(\)\s*===\s*"escuro"\s*\?\s*(\w+)\s*:\s*(\w+)\s*;'
)
JSON_PARSE_RE = re.compile(r"JSON\.parse\(([^)]*)\)")
DECLARACAO_ESC_RE = re.compile(r"function\s+esc\s*\(|const\s+esc\s*=")
CLASSE_DE_CARD_RE = re.compile(r'class="([^"]*rounded-sm[^"]*)"')
BG_SURFACE_RE = re.compile(r"(?<![\w-])bg-surface(?![\w-])")
DARK_BG_SURFACE_2_RE = re.compile(r"(?<![\w-])dark:bg-surface-2(?![\w-])")

RECADO_DE_FORMA = (
    "a forma do script de dashboard.html mudou; o resolvedor deste teste "
    "precisa acompanhar. NÃO relaxe o regex para que ele volte a passar sem "
    "casar nada — um gate de fonte que não acha o sítio que deveria medir "
    "passa verde sobre um defeito (foi assim que o G-04 atravessou a fase)."
)


def _texto_do_dashboard() -> str:
    return DASHBOARD.read_text(encoding="utf-8")


def _ligacoes(texto: str) -> dict[str, str]:
    """`ident -> "--cor-token"` para cada `const x = lerVarCss("--cor-y");`."""
    return dict(LIGACAO_RE.findall(texto))


def _classes_do_card_de(texto: str, id_grafico: str) -> str | None:
    """Classes do card que ENVOLVE o `<div id="{id_grafico}">`.

    Estratégia: recorta o texto antes do `id=`, e devolve o ÚLTIMO atributo
    `class="…"` que contenha `rounded-sm` — o marcador de card deste projeto.
    O que estiver entre o card e o gráfico (cabeçalho, `<h2>`, `<p>`) não usa
    `rounded-sm`, então o último acerto é o card mesmo.
    """
    marca = f'id="{id_grafico}"'
    corte = texto.find(marca)
    if corte == -1:
        return None
    achados = CLASSE_DE_CARD_RE.findall(texto[:corte])
    return achados[-1] if achados else None


class ResolucaoDoChromeTest(SimpleTestCase):
    """Metade 1: qual variável CSS cada elemento de cromo realmente lê."""

    def setUp(self):
        self.texto = _texto_do_dashboard()
        self.ligacoes = _ligacoes(self.texto)

    def test_o_resolvedor_encontra_as_ligacoes_lervarcss(self):
        self.assertTrue(
            bool(self.ligacoes),
            f"nenhuma ligação `const x = lerVarCss(\"--cor-…\")` encontrada — {RECADO_DE_FORMA}",
        )

    def test_o_resolvedor_encontra_o_sitio_da_grade_do_eixo(self):
        achados = SPLITLINE_RE.findall(self.texto)
        self.assertEqual(
            len(achados),
            1,
            f"esperado exatamente 1 `splitLine.lineStyle.color`, achados {achados!r} — {RECADO_DE_FORMA}",
        )
        self.assertIn(
            achados[0],
            self.ligacoes,
            f"`splitLine` usa `{achados[0]}`, que não é nenhuma ligação lerVarCss "
            f"conhecida ({sorted(self.ligacoes)}) — {RECADO_DE_FORMA}",
        )

    def test_o_resolvedor_encontra_o_sitio_da_borda_do_donut(self):
        achados = BORDERCOLOR_RE.findall(self.texto)
        self.assertEqual(
            len(achados),
            1,
            f"esperado exatamente 1 `itemStyle.borderColor`, achados {achados!r} — {RECADO_DE_FORMA}",
        )


class ContrasteDoChromeTest(SimpleTestCase):
    """Metade 2: o valor lido é visível contra o fundo REAL do card."""

    def setUp(self):
        self.texto = _texto_do_dashboard()
        self.ligacoes = _ligacoes(self.texto)
        self.tokens = dict(zip(("claro", "escuro"), tokens_do_input_css()))

    def _token_da_grade(self) -> str:
        achados = SPLITLINE_RE.findall(self.texto)
        self.assertEqual(len(achados), 1, RECADO_DE_FORMA)
        ident = achados[0]
        self.assertIn(ident, self.ligacoes, RECADO_DE_FORMA)
        return self.ligacoes[ident].removeprefix("--cor-")

    def test_grade_do_eixo_nao_e_o_mesmo_tom_do_card(self):
        """A asserção que fecha o gap: 1,00:1 é ausência de grade, não grade fraca."""
        grade = self._token_da_grade()
        for tema, chave_card in CARD_POR_TEMA.items():
            with self.subTest(tema=tema):
                razao = contraste(self.tokens[tema][grade], self.tokens[tema][chave_card])
                self.assertGreater(
                    razao,
                    1.0,
                    f"[{tema}] a grade do eixo lê `--cor-{grade}` "
                    f"({self.tokens[tema][grade]}) e o card é `--cor-{chave_card}` "
                    f"({self.tokens[tema][chave_card]}): contraste {razao:.2f}:1 — "
                    "mesmo tom, grade invisível (G-04)",
                )

    def test_grade_do_eixo_contrasta_com_o_fundo_real_do_card(self):
        grade = self._token_da_grade()
        for tema, chave_card in CARD_POR_TEMA.items():
            with self.subTest(tema=tema):
                razao = contraste(self.tokens[tema][grade], self.tokens[tema][chave_card])
                self.assertGreaterEqual(
                    razao,
                    PISO_CROMO,
                    f"[{tema}] grade `--cor-{grade}` sobre card `--cor-{chave_card}`: "
                    f"{razao:.2f}:1, abaixo do piso de cromo {PISO_CROMO}:1 "
                    "(a justificativa do piso está na docstring do módulo)",
                )


class MapeamentoDeElevacaoTest(SimpleTestCase):
    """A borda do donut acompanha o card, e o mapeamento bate com o HTML."""

    def setUp(self):
        self.texto = _texto_do_dashboard()
        self.ligacoes = _ligacoes(self.texto)

    def test_corcard_mapeia_a_elevacao_do_card_por_tema(self):
        achado = CORCARD_RE.search(self.texto)
        self.assertIsNotNone(
            achado,
            "não existe `const corCard = temaAtual() === \"escuro\" ? … : …;` no script — "
            "a cor do card precisa ser mapeada por tema, não fixada num nível de elevação. "
            f"{RECADO_DE_FORMA}",
        )
        ident_escuro, ident_claro = achado.group(1), achado.group(2)
        self.assertEqual(
            self.ligacoes.get(ident_escuro),
            f"--cor-{CARD_POR_TEMA['escuro']}",
            f"no escuro `corCard` deveria carregar --cor-{CARD_POR_TEMA['escuro']} "
            f"(o card é dark:bg-surface-2), mas carrega {self.ligacoes.get(ident_escuro)!r}",
        )
        self.assertEqual(
            self.ligacoes.get(ident_claro),
            f"--cor-{CARD_POR_TEMA['claro']}",
            f"no claro `corCard` deveria carregar --cor-{CARD_POR_TEMA['claro']} "
            f"(o card é bg-surface), mas carrega {self.ligacoes.get(ident_claro)!r}",
        )

    def test_borda_do_donut_usa_a_cor_do_card_mapeada_por_tema(self):
        achados = BORDERCOLOR_RE.findall(self.texto)
        self.assertEqual(len(achados), 1, RECADO_DE_FORMA)
        self.assertEqual(
            achados[0],
            "corCard",
            f"a separação entre as fatias do donut usa `{achados[0]}` — um nível de "
            "elevação fixo desenha, no escuro, linhas mais escuras que o card, que não "
            "existem no tema claro. Deve usar `corCard`.",
        )

    def test_cards_de_grafico_declaram_a_elevacao_que_o_script_assume(self):
        """Amarra `CARD_POR_TEMA` ao HTML: mudar o card sem mudar o script acusa aqui."""
        for id_grafico in IDS_DOS_GRAFICOS:
            with self.subTest(grafico=id_grafico):
                classes = _classes_do_card_de(self.texto, id_grafico)
                self.assertIsNotNone(
                    classes,
                    f"não achei o card que envolve `id=\"{id_grafico}\"` — {RECADO_DE_FORMA}",
                )
                self.assertRegex(
                    classes,
                    BG_SURFACE_RE,
                    f"o card de `{id_grafico}` não declara `bg-surface`; o mapeamento "
                    "do claro em corCard deixou de bater com o HTML",
                )
                self.assertRegex(
                    classes,
                    DARK_BG_SURFACE_2_RE,
                    f"o card de `{id_grafico}` não declara `dark:bg-surface-2`; o "
                    "mapeamento do escuro em corCard deixou de bater com o HTML",
                )


class SegurancaDoFormatterTest(SimpleTestCase):
    """WR-13: o retorno do `formatter` do ECharts é inserido como HTML."""

    def setUp(self):
        self.texto = _texto_do_dashboard()

    def test_funcao_de_escape_existe_no_script(self):
        # `assertIsNotNone(regex.search(...))`, e não `assertRegex(texto, ...)`:
        # o assert do unittest imprime o HAYSTACK inteiro na falha, e aqui o
        # haystack é o dashboard todo (12 KB). Um gate cuja mensagem de falha
        # precisa ser rolada por 12 KB de HTML é um gate que ninguém lê.
        self.assertIsNotNone(
            DECLARACAO_ESC_RE.search(self.texto),
            "os formatters chamam `esc(...)` mas a função não está declarada no script — "
            "um gate que só procurasse `esc(` passaria com uma chamada inexistente, que "
            "lança ReferenceError e derruba o tooltip",
        )

    def test_formatters_escapam_todo_nome_vindo_de_dado(self):
        for cru, escapado in (("${p.name}", "${esc(p.name)}"), ("${params.name}", "${esc(params.name)}")):
            with self.subTest(interpolacao=cru):
                # `assertFalse`/`assertTrue` sobre o booleano, pelo mesmo motivo
                # do teste acima: `assertIn`/`assertNotIn` despejariam o template.
                self.assertFalse(
                    cru in self.texto,
                    f"`{cru}` entra numa template string que o ECharts insere como HTML "
                    "e vem de `dict(Choices.choices).get(x, x)` — com fallback para o valor "
                    "CRU do banco (views.py). `choices` é validação de formulário, não "
                    "constraint de banco.",
                )
                self.assertTrue(
                    escapado in self.texto,
                    f"esperado `{escapado}` no formatter — todo valor de dado passa por escape",
                )


class RobustezDoJsonParseTest(SimpleTestCase):
    """IN-04: um `json_script` vazio não pode derrubar os dois gráficos."""

    def setUp(self):
        self.texto = _texto_do_dashboard()

    def test_todo_json_parse_tem_fallback_para_conteudo_vazio(self):
        chamadas = JSON_PARSE_RE.findall(self.texto)
        self.assertTrue(chamadas, f"nenhum `JSON.parse(` encontrado — {RECADO_DE_FORMA}")
        for argumento in chamadas:
            with self.subTest(argumento=argumento.strip()):
                self.assertIn(
                    "||",
                    argumento,
                    f"`JSON.parse({argumento.strip()})` não tem fallback: um `<script>` "
                    "vazio lança SyntaxError e derruba os DOIS gráficos",
                )
