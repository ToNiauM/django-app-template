"""Regressão do quick task 260818-n9k: comentários `{# #}` multilinha vazam.

O lexer de templates do Django (`tag_re` em `django.template.base`) casa
`{#...#}` SEM `re.DOTALL` — um comentário inline só é comentário se abrir e
fechar NA MESMA LINHA. Um `{# ... #}` que abrange múltiplas linhas é emitido
como texto literal no HTML servido ao cliente (vazamento de racional interno
de segurança, ver CR-01/T-02-11).

Este teste espelha exatamente essa semântica: remove do texto de cada
template todas as ocorrências de `\\{#.*?#\\}` sem DOTALL (o que o Django
descartaria) e então falha se restar qualquer `{#` ou `#}` — ou seja, falha
se alguém reintroduzir um comentário `{# #}` multilinha. Comentários de uma
linha continuam aceitos. Arquivos `.jinja` são ignorados de propósito: eles
passam pelo Jinja do Copier, cujos comentários multilinha são legais.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Mesma semântica do tag_re do Django: sem re.DOTALL, `.` não cruza linhas.
COMENTARIO_INLINE_VALIDO = re.compile(r"\{#.*?#\}")


def sobras_de_comentario(texto: str) -> list[str]:
    """Devolve as linhas com `{#`/`#}` que o Django NÃO trataria como comentário."""
    sem_comentarios_validos = COMENTARIO_INLINE_VALIDO.sub("", texto)
    return [
        f"linha {numero}: {linha.strip()}"
        for numero, linha in enumerate(
            sem_comentarios_validos.splitlines(), start=1
        )
        if "{#" in linha or "#}" in linha
    ]


def varrer_templates(diretorios: list[Path]) -> dict[str, list[str]]:
    """Varre `*.html` (nunca `.jinja`) e acumula sobras por arquivo."""
    problemas: dict[str, list[str]] = {}
    for diretorio in diretorios:
        if not diretorio.is_dir():
            continue
        for arquivo in sorted(diretorio.rglob("*.html")):
            sobras = sobras_de_comentario(
                arquivo.read_text(encoding="utf-8")
            )
            if sobras:
                try:
                    chave = str(arquivo.relative_to(ROOT))
                except ValueError:
                    chave = str(arquivo)
                problemas[chave] = sobras
    return problemas


class ComentariosMultilinhaTests(unittest.TestCase):
    def test_nenhum_template_html_tem_comentario_inline_multilinha(self):
        problemas = varrer_templates(
            [ROOT / "core" / "templates", ROOT / "apps"]
        )
        self.assertEqual(
            problemas,
            {},
            "Comentário `{# #}` multilinha detectado — o Django o emitirá "
            "como texto literal no HTML. Use {% comment %}...{% endcomment %}. "
            f"Ocorrências: {problemas}",
        )

    def test_ha_templates_para_varrer(self):
        # Sanidade: se a árvore de templates mudar de lugar, o teste acima
        # passaria em vácuo — este guarda garante que a varredura viu algo.
        templates = list((ROOT / "core" / "templates").rglob("*.html"))
        self.assertGreater(len(templates), 0)


if __name__ == "__main__":
    unittest.main()
