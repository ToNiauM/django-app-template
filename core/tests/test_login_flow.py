"""Prova viva das convenções de fundação (CORE-02/CFG-04): HTMX-redirect,
CSRF round-trip lido do cookie a cada request, lockout do django-axes sem
quebrar a convenção HTTP 200, e proteção contra open redirect em `?next=`.

Fonte: adaptado de /opt/web/pca/core/tests/test_login_flow.py — mesmas
convenções, sem nada de domínio.
"""

import re

from django.test import Client, TestCase, override_settings

from core.models import Usuario


@override_settings(SESSION_COOKIE_SECURE=False, CSRF_COOKIE_SECURE=False)
class LoginFlowTests(TestCase):
    def setUp(self):
        self.email = "usuario@exemplo.org"
        self.password = "correta-123"
        self.user = Usuario.objects.create_user(
            email=self.email, password=self.password
        )

    def test_get_login_sem_sessao_retorna_200_e_renderiza_login_html(self):
        client = Client()
        response = client.get("/login/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/login.html")

    def test_get_raiz_sem_sessao_redireciona_para_login_com_next(self):
        client = Client()
        response = client.get("/")
        self.assertRedirects(
            response, "/login/?next=/", fetch_redirect_response=False
        )

    def test_post_login_credenciais_validas_htmx_devolve_hx_redirect(self):
        client = Client()
        response = client.post(
            "/login/",
            {"email": self.email, "password": self.password},
            headers={"HX-Request": "true"},
        )
        self.assertEqual(response["HX-Redirect"], "/")
        # Sessão fica autenticada.
        self.assertIn("_auth_user_id", client.session)

    def test_post_login_credenciais_invalidas_nunca_4xx(self):
        client = Client()
        response = client.post(
            "/login/", {"email": "errado@exemplo.org", "password": "errada"}
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("E-mail ou senha inválidos.", content)

    def test_sexta_tentativa_consecutiva_bloqueada_permanece_200(self):
        client = Client()
        for _ in range(5):
            client.post(
                "/login/", {"email": self.email, "password": "senha-errada"}
            )

        response = client.post(
            "/login/", {"email": self.email, "password": "senha-errada"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("bloque", response.content.decode("utf-8").lower())

    def test_get_raiz_com_sessao_valida_renderiza_shell(self):
        client = Client()
        client.force_login(self.user)
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/shell.html")

    def test_post_logout_autenticado_devolve_hx_redirect_e_exige_login_de_novo(
        self,
    ):
        client = Client()
        client.force_login(self.user)

        response = client.post("/logout/", headers={"HX-Request": "true"})
        self.assertEqual(response["HX-Redirect"], "/login/")

        # Sessão encerrada — a raiz volta a exigir login.
        proxima = client.get("/")
        self.assertRedirects(
            proxima, "/login/?next=/", fetch_redirect_response=False
        )

    def test_csrf_round_trip_lido_do_cookie_a_cada_request(self):
        client = Client(enforce_csrf_checks=True)

        # 1ª visita: GET no login para receber o cookie csrftoken inicial.
        client.get("/login/")
        csrf_token = client.cookies["csrftoken"].value

        response = client.post(
            "/login/",
            {"email": self.email, "password": self.password},
            headers={"HX-Request": "true", "X-CSRFToken": csrf_token},
        )
        self.assertEqual(response["HX-Redirect"], "/")

    @staticmethod
    def _extrair_next_do_form(conteudo_html):
        """Extrai o valor do campo oculto `next` renderizado pelo form.

        Simula o que o navegador faz de verdade: lê o valor já presente no
        HTML devolvido pelo GET, em vez de montar a querystring do POST na
        mão (o que mascararia o bug do CR-01, em que o form nunca propagava
        `next`).
        """
        casado = re.search(r'name="next" value="([^"]*)"', conteudo_html)
        return casado.group(1) if casado else ""

    def test_next_legitimo_sobrevive_ao_ciclo_completo_get_form_post(self):
        # GET com `?next=` — como o `LoginRequiredMiddleware` produziria ao
        # redirecionar um acesso não autenticado a uma página protegida.
        client = Client()
        pagina_protegida = "/pagina-protegida/"
        resposta_get = client.get(f"/login/?next={pagina_protegida}")
        conteudo = resposta_get.content.decode("utf-8")

        # O campo oculto do form precisa carregar o `next` recebido no GET —
        # é o que prova que o valor realmente atravessa o template.
        next_no_form = self._extrair_next_do_form(conteudo)
        self.assertEqual(next_no_form, pagina_protegida)

        # POST real: só os campos que o form efetivamente envia, incluindo o
        # campo oculto extraído do HTML (não a querystring da URL).
        resposta_post = client.post(
            "/login/",
            {
                "email": self.email,
                "password": self.password,
                "next": next_no_form,
            },
            headers={"HX-Request": "true"},
        )
        self.assertEqual(resposta_post["HX-Redirect"], pagina_protegida)

    def test_next_open_redirect_nunca_aponta_para_host_externo(self):
        # Mesmo ciclo real GET→form→POST, mas com um `next` malicioso —
        # prova que a proteção contra open redirect também vale para o
        # caminho que a interface de fato produz, não só para um POST
        # direto forjado.
        client = Client()
        alvo_malicioso = "https://evil.example.com/"
        resposta_get = client.get(f"/login/?next={alvo_malicioso}")
        next_no_form = self._extrair_next_do_form(resposta_get.content.decode("utf-8"))
        self.assertEqual(next_no_form, alvo_malicioso)

        response = client.post(
            "/login/",
            {
                "email": self.email,
                "password": self.password,
                "next": next_no_form,
            },
            headers={"HX-Request": "true"},
        )
        self.assertEqual(response["HX-Redirect"], "/")
