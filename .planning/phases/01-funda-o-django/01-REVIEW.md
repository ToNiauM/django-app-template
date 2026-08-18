---
phase: 01-funda-o-django
reviewed: 2026-08-18T00:19:01Z
depth: standard
files_reviewed: 30
files_reviewed_list:
  - config/__init__.py
  - config/settings/__init__.py
  - config/settings/base.py
  - config/settings/dev.py
  - config/settings/prod.py
  - config/urls.py
  - config/wsgi.py
  - core/README.md
  - core/__init__.py
  - core/apps.py
  - core/axes_lockout.py
  - core/context_processors.py
  - core/middleware.py
  - core/migrations/0001_initial.py
  - core/migrations/__init__.py
  - core/models.py
  - core/static/src/input.css
  - core/templates/base.html
  - core/templates/core/_login_form.html
  - core/templates/core/login.html
  - core/templates/core/shell.html
  - core/tests/__init__.py
  - core/tests/test_auth.py
  - core/tests/test_login_flow.py
  - core/urls.py
  - core/views.py
  - manage.py
  - requirements.txt
  - .env.example
  - Dockerfile
  - compose.yml
  - entrypoint.sh
  - tailwind.config.js
  - .dockerignore
findings:
  critical: 2
  warning: 4
  info: 2
  total: 8
status: issues_found
---

# Phase 01: Code Review Report — Fundação Django

**Reviewed:** 2026-08-18T00:19:01Z
**Depth:** standard
**Files Reviewed:** 30 (core/static/vendor/*.min.js deliberadamente excluído — asset vendorizado)
**Status:** issues_found

## Summary

Revisão adversarial de todo o "walking skeleton" da Fase 1 (settings, kernel `core/`,
autenticação por e-mail, integração django-axes, casca HTMX, Docker/Compose). A
maior parte dos invariantes de segurança listados no escopo (Argon2 primeiro,
lockout do axes em HTTP 200, cookies Secure/HttpOnly/SameSite, `CSRF_COOKIE_HTTPONLY=False`
com leitura via `htmx:configRequest`, `DEBUG=False`/`ALLOWED_HOSTS` restrito em prod,
login por e-mail) **estão corretamente implementados e cobertos por teste**.

Dois problemas graves foram encontrados: (1) o parâmetro `?next=` — cuja proteção
contra open redirect é testada e comentada extensivamente no código — nunca chega a
ser usado na prática, porque nem a view nem os templates o propagam pelo ciclo
completo GET→POST do formulário de login; o resultado é que o recurso que o próprio
código diz proteger está, na prática, sempre inoperante (todo login bem-sucedido cai
em `/`, mesmo quando o usuário foi redirecionado de uma página protegida). (2) o
arquivo `core/tests/test_login_flow.py` menciona explicitamente "PCA" (via o caminho
`/opt/web/pca`) no docstring do módulo, violando o invariante "zero menção a PCA ou
qualquer domínio no código" declarado como obrigatório para este template.

Também foram encontrados pontos de robustez/hardening de infraestrutura (container
rodando como root, ausência de valor padrão seguro para o bind de porta do host,
posição do `AxesMiddleware` fora do padrão documentado pelo próprio django-axes sem
justificativa) que devem ser corrigidos ou, no mínimo, documentados antes de este
template ser clonado para sistemas reais.

## Critical Issues

### CR-01: `?next=` nunca é propagado — redirecionamento pós-login está quebrado na prática

**File:** `core/views.py:41-42` e `core/views.py:67`, `core/templates/core/_login_form.html:1`, `core/templates/core/login.html`

**Issue:**
O fluxo real de "sessão expirada → login → volta para a página que o usuário queria"
não funciona, apesar de o código conter proteção testada contra open redirect
(`url_has_allowed_host_and_scheme`, comentário `T-04-03`).

Passo a passo do bug:

1. `LoginRequiredMiddleware` redireciona um GET não autenticado para
   `/login/?next=/pagina-protegida/` (comportamento padrão do Django).
2. `login_view` no ramo GET devolve o template sem propagar `next` nenhum:
   ```python
   if request.method != "POST":
       return TemplateResponse(request, "core/login.html", {})
   ```
   (`core/views.py:41-42`) — o contexto é um dict vazio, `next` é descartado.
3. `core/templates/core/_login_form.html` não tem nenhum campo oculto `name="next"`
   e usa `hx-post="{% url 'core:login' %}"` — que resolve para `/login/` **sem**
   querystring (a tag `{% url %}` nunca herda a querystring da requisição atual).
4. Quando o usuário efetivamente submete o formulário via htmx, a requisição POST
   chega em `login_view` sem `next` em `request.GET` (a URL do POST é `/login/`,
   sem query string) **e** sem `next` em `request.POST` (não existe esse campo no
   form). Logo:
   ```python
   destino_bruto = request.GET.get("next") or request.POST.get("next")  # sempre None
   ```
   (`core/views.py:67`) — `destino` cai sempre no fallback `"/"`.

Confirma-se isso com um grep no próprio código: a string `"next"` só aparece dentro
de `core/views.py` — nenhum template usa/propaga esse valor.

O único teste que exercita esse caminho
(`test_next_open_redirect_nunca_aponta_para_host_externo` em
`core/tests/test_login_flow.py`) faz POST diretamente para
`"/login/?next=https://evil.example.com/"`, ou seja, simula uma requisição que a
interface real nunca produz (o form nunca inclui `next` na querystring do POST nem
como campo oculto). Isso dá falsa confiança: o teste passa, mas o recurso "voltar
para onde o usuário estava" nunca funcionou nem funcionaria em uso real — só o
branch de *bloqueio* do open redirect é exercitado, nunca o branch de sucesso com um
`next` legítimo.

**Fix:**
Propagar `next` do GET para o contexto do template, incluir como campo oculto no
form (que já é populado corretamente no POST body, sem precisar tocar na URL do
`hx-post`), e preservá-lo também no ramo de erro/bloqueio (senão se perde de novo na
segunda tentativa após uma senha errada):

```python
# core/views.py
if request.method != "POST":
    return TemplateResponse(
        request, "core/login.html", {"next": request.GET.get("next", "")}
    )

email = request.POST.get("email", "")
senha = request.POST.get("password", "")
next_bruto = request.POST.get("next", "")

user = authenticate(request, username=email, password=senha)

if user is None:
    bloqueado = bool(getattr(request, "axes_locked_out", False))
    return TemplateResponse(
        request,
        "core/_login_form.html",
        {
            "email": email,
            "next": next_bruto,
            "bloqueado": bloqueado,
            "erro": not bloqueado,
        },
        status=200,
    )

login(request, user)

destino_bruto = next_bruto or request.GET.get("next")
if destino_bruto and url_has_allowed_host_and_scheme(...):
    destino = destino_bruto
else:
    destino = "/"
```

```html
<!-- core/templates/core/_login_form.html -->
<form id="login-form" hx-post="{% url 'core:login' %}" hx-target="#login-form" hx-swap="outerHTML" ...>
  {% csrf_token %}
  <input type="hidden" name="next" value="{{ next|default:'' }}">
  ...
```

Recomenda-se também substituir o teste existente por um que exercite o ciclo real
(GET `/login/?next=...` → extrair o valor do campo oculto renderizado → POST com
esse valor), para que a cobertura reflita o comportamento de produção.

---

### CR-02: Menção explícita a "PCA" dentro do código-fonte — viola invariante de zero menção a domínio

**File:** `core/tests/test_login_flow.py:1-7` (linha 5)

**Issue:**
O invariante de projeto declarado para esta fase é explícito: "zero mention of 'PCA'
or any business domain in the code." O docstring do módulo de teste, no entanto,
cita o caminho de origem do sistema real:

```python
"""Prova viva das convenções de fundação (CORE-02/CFG-04): HTMX-redirect,
CSRF round-trip lido do cookie a cada request, lockout do django-axes sem
quebrar a convenção HTTP 200, e proteção contra open redirect em `?next=`.

Fonte: adaptado de /opt/web/pca/core/tests/test_login_flow.py — mesmas
convenções, sem nada de domínio.
"""
```

Isso é um vazamento concreto de proveniência do sistema de origem dentro do
template que deveria ser genérico e clonável — exatamente o tipo de menção que o
invariante do projeto proíbe, independente de estar "só" em um comentário/docstring.

**Fix:**
Remover a referência ao caminho `/opt/web/pca` do docstring. Por exemplo:

```python
"""Prova viva das convenções de fundação (CORE-02/CFG-04): HTMX-redirect,
CSRF round-trip lido do cookie a cada request, lockout do django-axes sem
quebrar a convenção HTTP 200, e proteção contra open redirect em `?next=`.
"""
```

## Warnings

### WR-01: Container de produção roda como root — sem diretiva `USER`

**File:** `Dockerfile:26-51`

**Issue:** O estágio `runtime` (`FROM python:3.12-slim AS runtime`) nunca cria nem
troca para um usuário não-privilegiado. O processo `gunicorn` definido em
`entrypoint.sh` acaba rodando como root dentro do container. Caso o processo da
aplicação seja comprometido (ex.: RCE via alguma dependência), o atacante herda
privilégios de root dentro do container — reduz a superfície de contenção que o
Docker oferece por padrão.

**Fix:**
```dockerfile
RUN groupadd -r app && useradd -r -g app -d /app app \
    && chown -R app:app /app
USER app
```
(inserir antes do `ENTRYPOINT`, garantindo que `chmod +x` e `collectstatic` já
tenham rodado como root antes da troca de usuário).

### WR-02: `WEB_BIND_ADDRESS`/`WEB_PORT` sem valor padrão seguro em `compose.yml`

**File:** `compose.yml:30`

**Issue:** O invariante de segurança do projeto exige que a aplicação fique "bound
to 127.0.0.1 on the host". Isso depende inteiramente de `.env` definir
`WEB_BIND_ADDRESS=127.0.0.1` (só documentado em `.env.example`, não reforçado em
`compose.yml`):
```yaml
ports:
  - "${WEB_BIND_ADDRESS}:${WEB_PORT}:8000"
```
Se `.env` for criado sem essa variável (erro humano comum ao clonar o template), o
Compose interpola uma string vazia, e o comportamento resultante do mapeamento de
porta passa a expor a aplicação em todas as interfaces (`0.0.0.0`) — quebrando
silenciosamente o invariante de segurança mais citado no contexto desta revisão, sem
nenhum aviso do Compose.

**Fix:**
```yaml
ports:
  - "${WEB_BIND_ADDRESS:-127.0.0.1}:${WEB_PORT:-8000}:8000"
```
Usar a sintaxe de valor padrão do Compose torna o invariante "seguro por padrão"
mesmo que o operador esqueça de definir a variável.

### WR-03: `AxesMiddleware` não é o último item de `MIDDLEWARE`, sem justificativa registrada

**File:** `config/settings/base.py:36-49`

**Issue:** A documentação oficial do django-axes é explícita: "`AxesMiddleware`
should be the last middleware in the `MIDDLEWARE` list." Neste projeto, ele aparece
antes de `MessageMiddleware` e `LoginRequiredMiddleware`:
```python
MIDDLEWARE = [
    ...
    "axes.middleware.AxesMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
]
```
O comentário do bloco afirma "a ordem do MIDDLEWARE é normativa — não reordenar sem
entender o motivo de cada posição", e de fato cada posição não-óbvia da lista tem um
comentário dedicado explicando o porquê — exceto esta, que contraria a recomendação
oficial da própria biblioteca sem nenhuma nota explicando por que é seguro desviar
dela aqui (o efeito prático hoje é mitigado porque `AXES_LOCKOUT_CALLABLE` neutraliza
a substituição de resposta que o `AxesMiddleware` faria, mas isso não está
documentado junto à declaração do `MIDDLEWARE`, criando risco de regressão silenciosa
se o callable for removido/alterado no futuro sem que alguém religue esse fio).

**Fix:** Mover `AxesMiddleware` para o final da lista (depois de
`LoginRequiredMiddleware`), ou — se há um motivo real para mantê-lo onde está —
adicionar um comentário explícito ao lado da linha explicando a exceção, como é
feito para todas as outras posições não-óbvias do arquivo.

### WR-04: `SILENCED_SYSTEM_CHECKS` em `prod.py` sem comentário — quebra o padrão de documentação do arquivo

**File:** `config/settings/prod.py:22`

**Issue:**
```python
SILENCED_SYSTEM_CHECKS = ["security.W005", "security.W021"]
```
`W005`/`W021` correspondem aos checks de sistema para
`SECURE_HSTS_INCLUDE_SUBDOMAINS`/`SECURE_HSTS_PRELOAD` (explicitamente `False` neste
mesmo arquivo). Todo o resto de `prod.py` e `base.py` documenta com comentário por
que cada escolha não-óbvia foi feita (ver `SECURE_REDIRECT_EXEMPT`,
`AXES_USERNAME_FORM_FIELD`, `CSRF_COOKIE_HTTPONLY`, etc.) — esta linha é a única
exceção, quebrando a convenção interna do próprio arquivo e dificultando que um
revisor futuro confirme que os dois checks silenciados correspondem exatamente às
duas flags de HSTS decididas conscientemente (e não, por exemplo, a outro warning de
segurança silenciado por engano).

**Fix:** Adicionar comentário explicando a relação direta com
`SECURE_HSTS_INCLUDE_SUBDOMAINS = False` / `SECURE_HSTS_PRELOAD = False` logo acima
da linha.

## Info

### IN-01: `HtmxRedirectMiddleware` assume que toda resposta 301/302 tem header `Location`

**File:** `core/middleware.py:20-21`

**Issue:**
```python
if getattr(request, "htmx", False) and response.status_code in (301, 302):
    return HttpResponseClientRedirect(response["Location"])
```
`response["Location"]` levanta `KeyError` se, por qualquer motivo (view customizada
futura, middleware de terceiros), uma resposta 301/302 chegar sem esse header. Hoje
não há tal caso no código (todos os redirects passam por `redirect_to_login()` ou por
`HttpResponseClientRedirect` explícito nas views, que sempre setam `Location`), mas é
um ponto frágil para regressões futuras.

**Fix:** `response.get("Location")` combinado com um fallback (ex.: devolver a
resposta original se o header não existir), para degradar sem 500 em vez de estourar
`KeyError`.

### IN-02: `{% csrf_token %}` duplicado com a leitura de cookie via JS — redundância não documentada

**File:** `core/templates/core/_login_form.html:3`, `core/templates/core/shell.html:14`, `core/templates/base.html:24-26`

**Issue:** Todo formulário submetido via htmx já recebe o header `X-CSRFToken`
injetado a cada requisição pelo listener global em `base.html` (`htmx:configRequest`).
Os formulários, além disso, também incluem `{% csrf_token %}` (campo oculto
`csrfmiddlewaretoken`), que a submissão htmx também envia no corpo. Isso não é
incorreto (o `CsrfViewMiddleware` aceita token via header OU corpo), mas é redundante
e não há comentário explicando se o campo oculto é deliberado (ex.: fallback para
submissão sem JS) ou apenas herdado do padrão Django sem necessidade real neste fluxo
100%-htmx.

**Fix:** Se o campo oculto for proposital (fallback no-JS), documentar isso com um
comentário breve — consistente com o padrão do restante do projeto de sempre
justificar decisões não-óbvias relacionadas a CSRF/htmx.

---

_Reviewed: 2026-08-18T00:19:01Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
