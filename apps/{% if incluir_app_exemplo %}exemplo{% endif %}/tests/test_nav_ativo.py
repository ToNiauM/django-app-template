"""Prova de renderização real do menu que o núcleo semeia (G-01 / NAV-01).

Este arquivo vive no app exemplo de propósito: as rotas `exemplo:*` só existem
quando `incluir_app_exemplo=true`, e um teste no `core` que dependesse delas
quebraria a geração sem o app.

O que se prova aqui não é a tag isolada, é o ARTEFATO: `core/_nav.html` mais o
`core/_nav_dominio.html` que o próprio template semeia, renderizados juntos com
um request de verdade. É a única forma de pegar a colisão do G-01 — dois itens
do stub (`exemplo:dashboard` → `/exemplo/dashboard/` e `exemplo:item_listar` →
`/exemplo/` com `prefixo="/exemplo/"`) acendendo ao mesmo tempo em
`/exemplo/dashboard/`.

`aria-current="page"` indica *a* localização atual: duas ocorrências na mesma
página contradizem a definição do atributo, além de desfazer o tratamento
visual inequívoco do item ativo (filete de 2px + `bg-brand-tint`).
"""

import re

from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse

# Cada <a ...> do menu, com atributos. `_item_nav.html` põe o aria-current
# dentro da própria tag de abertura, então casar a tag inteira permite dizer
# QUAL item está ativo, e não só quantos estão.
TAG_ANCORA = re.compile(r"<a\b[^>]*>", re.S)


class ItemAtivoUnicoNoMenuSemeadoTests(SimpleTestCase):
    """Renderiza `core/_nav.html` inteiro — núcleo + stub do domínio."""

    def setUp(self):
        self.factory = RequestFactory()

    def _menu(self, caminho):
        """Devolve (html, âncoras-ativas) para um request a `caminho`.

        `request=` é o que faz o context processor de request rodar e o
        `{% item_nav %}` enxergar `request.path`.
        """
        request = self.factory.get(caminho)
        html = render_to_string("core/_nav.html", request=request)
        ativas = [tag for tag in TAG_ANCORA.findall(html) if 'aria-current="page"' in tag]
        return html, ativas

    def _assere_unico_ativo(self, caminho, rota_esperada):
        html, ativas = self._menu(caminho)
        marcados = html.count('aria-current="page"')
        self.assertEqual(
            marcados,
            1,
            f"em {caminho} o menu marcou {marcados} itens como atuais; "
            "aria-current indica UMA localização",
        )
        self.assertEqual(len(ativas), 1)
        href_esperado = f'href="{reverse(rota_esperada)}"'
        self.assertIn(
            href_esperado,
            ativas[0],
            f"em {caminho} o item ativo não é {rota_esperada}: {ativas[0]}",
        )

    def test_em_dashboard_apenas_o_item_dashboard_fica_ativo(self):
        """O defeito do G-01, na forma exata em que ele aparece."""
        self._assere_unico_ativo("/exemplo/dashboard/", "exemplo:dashboard")

    def test_na_listagem_apenas_o_item_de_itens_fica_ativo(self):
        self._assere_unico_ativo("/exemplo/", "exemplo:item_listar")

    def test_em_rota_filha_sem_item_proprio_o_prefixo_continua_valendo(self):
        """O conserto não pode ser 'desligar o prefixo'.

        `/exemplo/42/editar/` não tem item próprio no menu; quem deve acender
        é "Itens (CRUD)", pelo `prefixo="/exemplo/"`.
        """
        self._assere_unico_ativo("/exemplo/42/editar/", "exemplo:item_listar")

    def test_o_stub_semeado_declara_os_dois_itens_do_exemplo(self):
        """Guarda do próprio teste: sem os dois itens, os casos acima
        passariam por ausência em vez de por desempate."""
        html, _ = self._menu("/exemplo/dashboard/")
        self.assertIn(f'href="{reverse("exemplo:dashboard")}"', html)
        self.assertIn(f'href="{reverse("exemplo:item_listar")}"', html)
        self.assertIn("Dashboard", html)
        self.assertIn("Itens (CRUD)", html)
