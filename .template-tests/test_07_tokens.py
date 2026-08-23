"""Contrato dos tokens de cor da Fase 7 — sobre a FONTE, nunca sobre o CSS
compilado (Pitfall 4: `dark:` compila para `:where(...)`, forma variável).
"""

from __future__ import annotations

import re
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

TEMPLATE_DIRS = ("core/templates", "apps")


def _iter_template_files():
    for directory in TEMPLATE_DIRS:
        base = ROOT / directory
        if not base.exists():
            continue
        yield from base.rglob("*.html")


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
        text_secundaria_re = re.compile(r"text-secundaria\b")
        secundaria_uso_re = re.compile(r"\b((?:bg|border|fill|text)-secundaria)\b")

        ocorrencias_texto = []
        ocorrencias_fora_do_contrato = []
        for path in _iter_template_files():
            texto = path.read_text(encoding="utf-8", errors="ignore")
            if text_secundaria_re.search(texto):
                ocorrencias_texto.append(str(path.relative_to(ROOT)))
            for match in secundaria_uso_re.finditer(texto):
                if match.group(1).startswith("text-"):
                    ocorrencias_fora_do_contrato.append(
                        f"{path.relative_to(ROOT)}: {match.group(1)}"
                    )

        self.assertEqual(ocorrencias_texto, [])
        self.assertEqual(ocorrencias_fora_do_contrato, [])

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

        # Todo sufixo de tamanho que o Tailwind reconhece nativamente — usado
        # só para decidir se um match de `text-<sufixo>` é candidato a
        # tamanho de fonte (e portanto tem que estar na régua) ou é uma
        # classe de outro vocabulário (cor, alinhamento) e deve ser ignorada.
        TAMANHOS_TAILWIND_CONHECIDOS = {
            "xs", "sm", "base", "md", "lg", "xl",
            "2xl", "3xl", "4xl", "5xl", "6xl", "7xl", "8xl", "9xl",
        }
        TEXT_CLASS_RE = re.compile(r"\btext-([a-z0-9]+|\[[^\]]+\])\b")

        ofensores = []
        for path in _iter_template_files():
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
                        ofensores.append(
                            f"{path.relative_to(ROOT)}:{numero_linha} text-{sufixo}"
                        )

        self.assertEqual(ofensores, [], "\n".join(ofensores))


if __name__ == "__main__":
    unittest.main()
