"""Contrato dos tokens de cor da Fase 7 — sobre a FONTE, nunca sobre o CSS
compilado (Pitfall 4: `dark:` compila para `:where(...)`, forma variável).
"""

from __future__ import annotations

import importlib.util
import re
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT_CSS = ROOT / "core/static/src/input.css"
DOMINIO_CSS = ROOT / "core/static/src/dominio.css"
TAILWIND_CONFIG = ROOT / "tailwind.config.js"
TAILWIND_CONFIG_JINJA = ROOT / "tailwind.config.js.jinja"

HEX_TOKEN_RE = re.compile(r"--cor-([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})\s*;")

# Tokens migrados para var(--cor-*) — nenhum deles pode receber modificador
# de opacidade (`/NN`): o Tailwind não gera regra para var() com alpha.
MIGRATED_TOKENS = (
    "page|surface|surface-2|surface-3|ink|ink-2|muted|grid|baseline|brand|"
    "brand-hover|brand-ink|brand-tint|destructive|danger-tint|warn-bg|"
    "warn-tx|secundaria|seq-600|seq-450|seq-300"
)
OPACITY_MODIFIER_RE = re.compile(
    rf"(?:bg|text|border|ring|from|to|via)-(?:{MIGRATED_TOKENS})/[0-9]+"
)

# Todo sufixo de tamanho que o Tailwind reconhece nativamente — usado só para
# decidir se um match de `text-<sufixo>` é candidato a tamanho de fonte (e
# portanto tem que estar na régua) ou é uma classe de outro vocabulário (cor,
# alinhamento) e deve ser ignorada.
TAMANHOS_TAILWIND_CONHECIDOS = {
    "xs", "sm", "base", "md", "lg", "xl",
    "2xl", "3xl", "4xl", "5xl", "6xl", "7xl", "8xl", "9xl",
}

# Duas correções em relação ao padrão original (G-05 / CR-04), que era
# `r"\btext-([a-z0-9]+|\[[^\]]+\])\b"`:
#
# (a) a alternativa de valor arbitrário vem PRIMEIRO. O `re` tenta as
#     alternativas na ordem escrita e para na primeira que serve; com
#     `[a-z0-9]+` na frente, `text-[13px]` nem chegava ao segundo ramo.
# (b) o `\b` final virou lookahead negativo `(?![\w-])`. `\b` exige transição
#     entre caractere de palavra e não-palavra, e `]` JÁ é não-palavra: seguido
#     de `"` ou espaço não há transição nenhuma, então o ramo de colchete era
#     inalcançável e `class="text-[13px]"` devolvia lista vazia.
#
# O lookahead também recusa `text-ink-2` (o hífen continua a classe — é cor,
# não tamanho), que o `\b` deixava passar como `text-ink`. Efeito colateral
# correto: a string artificial `text-[13px]x` deixa de casar; não existe classe
# assim, o `\b` antigo só casava lá por acidente.
TEXT_CLASS_RE = re.compile(r"\btext-(\[[^\]]*\]|[a-z0-9]+)(?![\w-])")

TEMPLATE_DIRS = ("core/templates", "apps")


def _iter_template_files():
    for directory in TEMPLATE_DIRS:
        base = ROOT / directory
        if not base.exists():
            continue
        yield from base.rglob("*.html")


def varrer_classes_de_texto(paths, chaves_da_regua) -> list[str]:
    """Varre os arquivos recebidos e devolve os ofensores da régua tipográfica.

    Cada ofensor é uma string `"<caminho>:<linha> text-<sufixo>"` — arquivo e
    linha entram na mensagem porque um gate que só diz "há violação" obriga
    quem o vê a repetir a busca à mão.

    Um match de `text-<sufixo>` só é candidato quando o sufixo é valor
    arbitrário (`[24px]`) ou um tamanho que o Tailwind reconhece nativamente;
    `text-white`, `text-ink-2` e `text-center` são de outros vocabulários e
    passam. É função de módulo, e não corpo do método de teste, para que o
    teste da PRÓPRIA guarda possa exercitá-la — uma cópia do algoritmo dentro
    do teste não provaria nada sobre o gate.
    """
    ofensores: list[str] = []
    for path in paths:
        texto = path.read_text(encoding="utf-8", errors="ignore")
        for numero_linha, linha in enumerate(texto.splitlines(), start=1):
            for match in TEXT_CLASS_RE.finditer(linha):
                sufixo = match.group(1)
                e_valor_arbitrario = sufixo.startswith("[")
                e_tamanho_conhecido = sufixo in TAMANHOS_TAILWIND_CONHECIDOS
                if not (e_valor_arbitrario or e_tamanho_conhecido):
                    # cor (ink, ink-2, muted, brand, white, emerald-800…)
                    # ou alinhamento (left, center) — fora do escopo
                    continue
                if sufixo not in chaves_da_regua:
                    try:
                        rotulo = path.relative_to(ROOT)
                    except ValueError:
                        # caminho de fora do repositório (o teste da guarda
                        # usa um TemporaryDirectory) — reporta o caminho cru
                        rotulo = path
                    ofensores.append(f"{rotulo}:{numero_linha} text-{sufixo}")
    return ofensores


def _extract_block(css: str, selector_pattern: str) -> str:
    """Extrai o conteúdo de um bloco `seletor { ... }` de nível único.

    Aceita fechamento indentado (`\n      },`) — as chaves internas de uma
    só linha (ex.: `{ lineHeight: "1.4" }`) não têm quebra de linha antes
    delas, então o primeiro `\n` seguido (com indentação opcional) de `}`
    é sempre o fechamento do bloco de nível único procurado.
    """
    match = re.search(rf"{selector_pattern} \{{(.*?)\n\s*\}}", css, re.DOTALL)
    assert match is not None, f"bloco {selector_pattern!r} não encontrado"
    return match.group(1)


def _extract_array_block(css: str, selector_pattern: str) -> str:
    """Igual a `_extract_block`, mas para `seletor: [ ... ]`."""
    match = re.search(rf"{selector_pattern} \[(.*?)\n\s*\]", css, re.DOTALL)
    assert match is not None, f"bloco de array {selector_pattern!r} não encontrado"
    return match.group(1)


def _tokens_in_block(block: str) -> dict[str, str]:
    return {name: value for name, value in HEX_TOKEN_RE.findall(block)}


class TokensFonteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.css = INPUT_CSS.read_text(encoding="utf-8")

    def test_import_dominio_e_a_primeira_linha(self) -> None:
        primeira_linha = self.css.splitlines()[0]
        self.assertEqual(primeira_linha, '@import "./dominio.css";')
        self.assertTrue(DOMINIO_CSS.is_file())

    def test_root_declara_21_tokens_e_escuro_declara_18_overrides(self) -> None:
        root_block = _extract_block(self.css, ":root")
        escuro_block = _extract_block(self.css, r'\[data-tema="escuro"\]')

        root_tokens = _tokens_in_block(root_block)
        escuro_tokens = _tokens_in_block(escuro_block)

        self.assertEqual(len(root_tokens), 21, root_tokens)
        self.assertEqual(len(escuro_tokens), 18, escuro_tokens)

        # baseline, destructive e secundaria herdam do claro — não redeclarados
        for herda in ("baseline", "destructive", "secundaria"):
            self.assertNotIn(herda, escuro_tokens)

        # nenhum valor é color-mix()/rgb() com canal alfa variável — o regex
        # de captura já exige hex plano; aqui só confirmamos ausência literal
        self.assertNotIn("color-mix", self.css)
        self.assertNotIn("<alpha-value>", self.css)

    def test_tailwind_config_verbatim_e_toda_cor_tem_variavel_em_root(self) -> None:
        self.assertFalse(TAILWIND_CONFIG_JINJA.exists())
        self.assertTrue(TAILWIND_CONFIG.is_file())

        config = TAILWIND_CONFIG.read_text(encoding="utf-8")
        colors_block = _extract_block(config, "colors:")
        config_keys = set(re.findall(r'"?([a-z0-9-]+)"?:\s*"var\(--cor-([a-z0-9-]+)\)"', colors_block))
        # cada entrada é (chave_config, variavel); a chave e a variável têm
        # que ser o mesmo nome semântico
        config_names = {chave for chave, _variavel in config_keys}
        config_vars = {variavel for _chave, variavel in config_keys}
        self.assertEqual(
            config_names,
            config_vars,
            "toda chave de colors deve apontar para var(--cor-<mesma-chave>)",
        )

        root_block = _extract_block(self.css, ":root")
        root_tokens = set(_tokens_in_block(root_block).keys())

        faltando_no_root = config_vars - root_tokens
        sobrando_no_root = root_tokens - config_vars
        self.assertEqual(faltando_no_root, set(), "chave do config sem var em :root")
        self.assertEqual(
            sobrando_no_root, set(), "token em :root sem chave correspondente no config"
        )

    def test_fontsize_e_borderradius_tem_as_chaves_do_contrato(self) -> None:
        config = TAILWIND_CONFIG.read_text(encoding="utf-8")

        font_size_block = _extract_block(config, "fontSize:")
        font_size_keys = set(
            re.findall(r'^\s*"?([a-zA-Z0-9]+)"?:', font_size_block, re.MULTILINE)
        )
        self.assertEqual(font_size_keys, {"xs", "sm", "base", "md", "lg", "xl"})
        self.assertNotIn("2xl", font_size_keys)

        border_radius_block = _extract_block(config, "borderRadius:")
        border_radius_keys = set(
            re.findall(r'^\s*(DEFAULT|"?2xl"?|[a-zA-Z]+):', border_radius_block, re.MULTILINE)
        )
        border_radius_keys = {k.strip('"') for k in border_radius_keys}
        self.assertEqual(border_radius_keys, {"DEFAULT", "sm", "md", "lg", "xl", "2xl"})
        self.assertNotIn("none", border_radius_keys)
        self.assertNotIn("full", border_radius_keys)
        for match in re.finditer(r':\s*"([^"]+)"', border_radius_block):
            self.assertEqual(match.group(1), "2px")

    def test_safelist_bate_com_as_classes_declaradas_em_input_css(self) -> None:
        config = TAILWIND_CONFIG.read_text(encoding="utf-8")
        safelist_block = _extract_array_block(config, "safelist:")
        safelist_entries = set(re.findall(r'"([a-zA-Z0-9-]+(?:--[a-zA-Z]+)?)"', safelist_block))

        # Alternativas mais específicas primeiro: a alternação de regex casa
        # a primeira opção que bate, então "btn" sozinho capturaria só o
        # prefixo de "btn--primaria" se viesse antes dela na lista.
        component_classes = set(
            re.findall(
                r"\.(btn--primaria|btn--secundaria|btn--neutro|btn--destrutiva|"
                r"results|module|form-row|btn)\b",
                self.css,
            )
        )

        faltando_no_css = safelist_entries - component_classes
        faltando_na_safelist = component_classes - safelist_entries
        self.assertEqual(faltando_no_css, set(), "entrada da safelist sem classe em input.css")
        self.assertEqual(
            faltando_na_safelist, set(), "classe de input.css sem entrada na safelist"
        )
        self.assertEqual(len(safelist_entries), 8)

    def test_gate_de_opacidade_sobre_token_migrado(self) -> None:
        ocorrencias = []
        for path in _iter_template_files():
            texto = path.read_text(encoding="utf-8", errors="ignore")
            for match in OPACITY_MODIFIER_RE.finditer(texto):
                ocorrencias.append(f"{path.relative_to(ROOT)}: {match.group(0)}")
        self.assertEqual(ocorrencias, [])

    def test_gate_shadow_xs_nao_sobrevive_nos_templates(self) -> None:
        ocorrencias = []
        for path in _iter_template_files():
            texto = path.read_text(encoding="utf-8", errors="ignore")
            if "shadow-xs" in texto:
                ocorrencias.append(str(path.relative_to(ROOT)))
        self.assertEqual(ocorrencias, [])

    def test_gate_dourado_secundaria_e_forma_nunca_texto(self) -> None:
        """O dourado é FORMA, nunca TINTA (input.css: 3,99:1 sobre as
        superfícies claras reprova AA de texto).

        Duas asserções com escopos diferentes de propósito. A primeira é o
        caso explícito de D-86: `text-secundaria` em qualquer template. A
        segunda audita QUALQUER prefixo utilitário antes de `-secundaria` e
        reprova todo o que não esteja em `PREFIXOS_DE_FORMA` — antes ela
        descartava por prefixo tudo o que não fosse `text-`, e era portanto,
        logicamente, uma cópia da primeira (WR-08). Agora `ring-`, `decoration-`, `divide-`, `caret-`,
        `placeholder-`, `outline-`, `accent-` e `shadow-secundaria` reprovam
        junto: todos pintam tinta ou traço fino sobre superfície clara, que é
        exatamente o uso que o contraste do dourado não sustenta.
        """
        PREFIXOS_DE_FORMA = {"bg", "border", "fill"}
        text_secundaria_re = re.compile(r"text-secundaria\b")
        secundaria_uso_re = re.compile(r"\b([a-z-]+)-secundaria\b")

        ocorrencias_texto = []
        ocorrencias_fora_do_contrato = []
        for path in _iter_template_files():
            texto = path.read_text(encoding="utf-8", errors="ignore")
            if text_secundaria_re.search(texto):
                ocorrencias_texto.append(str(path.relative_to(ROOT)))
            for match in secundaria_uso_re.finditer(texto):
                prefixo = match.group(1)
                if prefixo not in PREFIXOS_DE_FORMA:
                    ocorrencias_fora_do_contrato.append(
                        f"{path.relative_to(ROOT)}: {prefixo}-secundaria"
                    )

        self.assertEqual(ocorrencias_texto, [])
        self.assertEqual(ocorrencias_fora_do_contrato, [])

    def test_o_gate_do_dourado_reprova_prefixo_fora_de_bg_border_fill(self) -> None:
        """A prova da própria guarda do WR-08: as strings que ela precisa
        classificar viram asserção, em vez de confiança. Sem este teste, o
        filtro poderia voltar a olhar só o prefixo `text-` sem que nada
        acusasse.
        """
        secundaria_uso_re = re.compile(r"\b([a-z-]+)-secundaria\b")
        esperado = {
            'class="bg-secundaria"': "bg",
            'class="border-secundaria"': "border",
            'class="fill-secundaria"': "fill",
            'class="text-secundaria"': "text",
            'class="ring-secundaria"': "ring",
            'class="decoration-secundaria"': "decoration",
            'class="divide-secundaria"': "divide",
            'class="caret-secundaria"': "caret",
            'class="placeholder-secundaria"': "placeholder",
            'class="outline-secundaria"': "outline",
            'class="accent-secundaria"': "accent",
            'class="shadow-secundaria"': "shadow",
        }
        for entrada, prefixo in esperado.items():
            with self.subTest(entrada=entrada):
                self.assertEqual(secundaria_uso_re.findall(entrada), [prefixo])

    def test_templates_so_usam_as_seis_chaves_da_regua_tipografica(self) -> None:
        """A régua tipográfica (07-02) só vale se nenhum template puder
        escapar dela. `.btn` usa `text-[13px]` dentro de
        `core/static/src/input.css` de propósito — é a única exceção a
        tamanho arbitrário permitida no vocabulário de componente do padrão,
        e vive no CSS, não em template; este gate varre só **templates**
        (`core/templates/**/*.html` e `apps/**/*.html`).
        """
        config = TAILWIND_CONFIG.read_text(encoding="utf-8")
        font_size_block = _extract_block(config, "fontSize:")
        chaves_da_regua = set(
            re.findall(r'^\s*"?([a-zA-Z0-9]+)"?:', font_size_block, re.MULTILINE)
        )
        self.assertEqual(chaves_da_regua, {"xs", "sm", "base", "md", "lg", "xl"})

        ofensores = varrer_classes_de_texto(_iter_template_files(), chaves_da_regua)

        self.assertEqual(ofensores, [], "\n".join(ofensores))

    def test_o_gate_da_regua_enxerga_valor_arbitrario(self) -> None:
        """A prova que faltava (G-05): as strings que o gate precisa detectar
        viram asserção.

        Com o regex antigo (`\\btext-([a-z0-9]+|\\[[^\\]]+\\])\\b`) as três
        primeiras linhas desta tabela devolvem `[]` — o `\\b` depois de `]`
        torna o ramo de valor arbitrário inalcançável. Este teste falha
        contra aquele regex e passa contra o atual; é essa diferença, e não a
        existência do teste, que fecha o gap.
        """
        esperado = {
            'class="text-[13px] font-bold"': ["[13px]"],
            'class="font-bold text-[13px]"': ["[13px]"],
            "class='text-[20px]'": ["[20px]"],
            'class="text-2xl"': ["2xl"],
            # cor, não tamanho: o hífen continua a classe e o lookahead recusa
            'class="text-ink-2"': [],
            # casa, mas "white" não é tamanho conhecido → o gate ignora
            'class="text-white"': ["white"],
        }
        for entrada, grupos in esperado.items():
            with self.subTest(entrada=entrada):
                self.assertEqual(TEXT_CLASS_RE.findall(entrada), grupos)

    def test_o_gate_da_regua_reporta_arquivo_e_linha_de_um_ofensor(self) -> None:
        """O ofensor sintético vive num diretório temporário, nunca em
        `core/templates/`: um `.html` solto dentro da árvore varrida
        contaminaria os outros gates se a limpeza falhasse.
        """
        chaves_da_regua = {"xs", "sm", "base", "md", "lg", "xl"}
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "x.html"
            alvo.write_text(
                '<div>\n<p class="text-[24px]">x</p>\n</div>\n', encoding="utf-8"
            )
            ofensores = varrer_classes_de_texto([alvo], chaves_da_regua)

        self.assertEqual(len(ofensores), 1, ofensores)
        self.assertTrue(
            ofensores[0].endswith(":2 text-[24px]"),
            f"esperava arquivo:linha e a classe ofensora, veio {ofensores[0]!r}",
        )

    def test_o_helper_de_contraste_e_carregavel_desta_suite(self) -> None:
        """A ponte entre as duas famílias de suíte, provada em wave 1.

        `core/tests/contraste.py` é a implementação ÚNICA da fórmula WCAG do
        repositório: ele vive dentro do sistema gerado (`.template-tests/`
        está em `_exclude` do copier.yml e não chega a derivado nenhum) e as
        suítes daqui o carregam por caminho. Este teste não mede design — ele
        só garante que a ponte existe e funciona. Se o arquivo for movido ou
        renomeado, quem descobre é este gate, agora, e não um plano de wave 3
        que já assume o helper de pé.
        """
        caminho = ROOT / "core/tests/contraste.py"
        self.assertTrue(caminho.exists(), f"helper de contraste ausente: {caminho}")

        spec = importlib.util.spec_from_file_location("contraste_wcag", caminho)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)

        self.assertEqual(modulo.contraste("#ffffff", "#000000"), 21.0)


if __name__ == "__main__":
    unittest.main()
