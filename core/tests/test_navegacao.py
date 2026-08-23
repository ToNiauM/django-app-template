"""Prova da inclusion tag {% item_nav %} (NAV-01/NAV-02/NAV-03): resolve rota
opcional sem quebrar (T-07-08), escapa o rótulo (T-07-05) e nunca aceita
markup de ícone como argumento (T-07-06) — ver core/templatetags/navegacao.py.
"""

from django.template import Context, Template
from django.test import RequestFactory, SimpleTestCase


class ItemNavTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _renderizar(self, request, rota, rotulo, icone="", prefixo=""):
        template = Template(
            "{% load navegacao %}"
            "{% item_nav rota rotulo icone prefixo %}"
        )
        contexto = Context(
            {
                "request": request,
                "rota": rota,
                "rotulo": rotulo,
                "icone": icone,
                "prefixo": prefixo,
            }
        )
        return template.render(contexto)

    def test_rota_existente_com_path_igual_a_url_fica_ativo(self):
        request = self.factory.get("/")

        html = self._renderizar(request, "core:shell", "Início", "casa")

        self.assertIn('aria-current="page"', html)
        self.assertIn("bg-brand-tint text-brand-ink", html)

    def test_rota_existente_com_path_diferente_fica_inativo(self):
        request = self.factory.get("/login/")

        html = self._renderizar(request, "core:shell", "Início", "casa")

        self.assertNotIn('aria-current="page"', html)
        self.assertIn("text-ink-2 hover:bg-surface-2", html)

    def test_prefixo_marca_ativo_em_rota_filha(self):
        request = self.factory.get("/exemplo/42/editar/")

        html = self._renderizar(
            request, "core:shell", "Itens", "lista", "/exemplo/"
        )

        self.assertIn('aria-current="page"', html)

    def test_rota_inexistente_nao_levanta_e_renderiza_vazio(self):
        request = self.factory.get("/")

        html = self._renderizar(request, "inexistente:rota", "Fantasma")

        self.assertEqual(html.strip(), "")
        self.assertNotIn("<a", html)

    def test_icone_desconhecido_renderiza_item_sem_svg_e_sem_erro(self):
        request = self.factory.get("/")

        html = self._renderizar(request, "core:shell", "Início", "nao-existe")

        self.assertIn("<a", html)
        self.assertIn("<span>Início</span>", html)
        self.assertNotIn("<svg", html)

    def test_rotulo_com_script_sai_escapado(self):
        request = self.factory.get("/")

        html = self._renderizar(request, "core:shell", "<script>alert(1)</script>")

        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)
