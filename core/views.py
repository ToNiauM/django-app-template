from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_not_required
from django.db import connection
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django_htmx.http import HttpResponseClientRedirect


@login_not_required
def healthz(request):
    """Rota de healthcheck (usada pelo `compose.yml` — Plan 01-03).

    Sem `@login_not_required`, o `LoginRequiredMiddleware` (Pitfall 9)
    redirecionaria toda requisição sem sessão para `/login/`, quebrando o
    healthcheck do container.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "error"}, status=503)
    return JsonResponse({"status": "ok"})


@login_not_required
def login_view(request):
    """GET renderiza a tela de login; POST autentica via htmx (CORE-02).

    Nunca envolve `authenticate()` com `except PermissionDenied`: o
    dispatcher de alto nível do Django (`django.contrib.auth.authenticate`)
    captura o `PermissionDenied` que o `AxesBackend` levanta internamente e
    NUNCA o repassa para quem chamou — só devolve `None` (comportamento
    documentado). A forma correta de distinguir "bloqueado pelo axes" de
    "credenciais erradas comuns" é o atributo `request.axes_locked_out`, que
    o `AxesBackend` seta no request antes de levantar (e sobrevive à captura
    silenciosa do dispatcher) — ver Pitfall 3/4 do 01-RESEARCH.md.
    """
    if request.method != "POST":
        return TemplateResponse(request, "core/login.html", {})

    email = request.POST.get("email", "")
    senha = request.POST.get("password", "")

    user = authenticate(request, username=email, password=senha)

    if user is None:
        bloqueado = bool(getattr(request, "axes_locked_out", False))
        return TemplateResponse(
            request,
            "core/_login_form.html",
            {
                "email": email,
                "bloqueado": bloqueado,
                "erro": not bloqueado,
            },
            status=200,  # nunca 4xx puro — htmx não faz swap por padrão (Pitfall 1)
        )

    login(request, user)

    # Proteção contra open redirect (T-04-03): `?next=` é entrada controlada
    # pelo cliente. `url_has_allowed_host_and_scheme` garante que só um
    # caminho relativo ao próprio host é aceito como destino.
    destino_bruto = request.GET.get("next") or request.POST.get("next")
    if destino_bruto and url_has_allowed_host_and_scheme(
        destino_bruto,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        destino = destino_bruto
    else:
        destino = "/"

    return HttpResponseClientRedirect(destino)  # nunca redirect() puro (Pitfall 2)


@require_POST
def logout_view(request):
    logout(request)
    return HttpResponseClientRedirect("/login/")


def shell_view(request):
    """Casca autenticada mínima desta fase.

    Sem `@login_not_required`: precisa de sessão válida, o que o
    `LoginRequiredMiddleware` já garante por padrão (Pitfall 9). A casca
    completa com navegação/breadcrumbs é `CORE-04`, Fase 2 — aqui só existe
    a prova de que o Walking Skeleton autentica de ponta a ponta.
    """
    return TemplateResponse(request, "core/shell.html", {})
