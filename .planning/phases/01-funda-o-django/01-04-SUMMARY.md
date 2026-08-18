---
phase: 01-funda-o-django
plan: 04
subsystem: auth
tags: [django, htmx, csrf, django-axes, login, logout, open-redirect]

# Dependency graph
requires:
  - phase: 01-01
    provides: "settings base (AUTHENTICATION_BACKENDS, AXES_*, CSRF cookie flags, LoginRequiredMiddleware)"
  - phase: 01-02
    provides: "core.Usuario/UsuarioManager, core.axes_lockout.resposta_bloqueio, HtmxRedirectMiddleware, context_processors.usuario_atual, core/views.py (healthz), config/urls.py (admin+healthz), core/templates/base.html (htmx:configRequest)"
  - phase: 01-03
    provides: "Docker Compose (web+db) funcional, migração 0001 do Usuario, PostgreSQL real, superusuário admin@sistemabase.local já criado"
provides:
  - "core.views.login_view/logout_view/shell_view — fatia vertical completa de login/logout via HTMX"
  - "core/urls.py (app_name=core) + config/urls.py com include('core.urls')"
  - "core/templates/core/login.html, _login_form.html, shell.html — templates mínimas e funcionais"
  - "core/tests/test_login_flow.py + test_auth.py — prova comportamental de HTMX-redirect/CSRF round-trip/lockout axes/open-redirect"
affects: ["01-05", "CORE-04 (Fase 2 — casca completa com navegação)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "login_view distingue 'bloqueado pelo axes' de 'senha errada comum' via request.axes_locked_out (nunca except PermissionDenied em torno de authenticate())"
    - "Redirect pós-login validado com django.utils.http.url_has_allowed_host_and_scheme(allowed_hosts={request.get_host()}) antes de aceitar ?next= — proteção contra open redirect"
    - "login_view/logout_view sempre HttpResponseClientRedirect (nunca redirect() puro) — HtmxRedirectMiddleware cobre o caso genérico residual"
    - "Credenciais inválidas e lockout do axes sempre HTTP 200 com fragmento re-renderizado (erro/bloqueado no contexto) — nunca 4xx"

key-files:
  created:
    - core/urls.py
    - core/tests/__init__.py
    - core/tests/test_login_flow.py
    - core/tests/test_auth.py
    - core/templates/core/login.html
    - core/templates/core/_login_form.html
    - core/templates/core/shell.html
  modified:
    - core/views.py
    - config/urls.py

key-decisions:
  - "Padrão de view/teste reproduzido verbatim de /opt/web/pca (fonte de extração em produção), generalizado e sem menção a domínio"
  - "Templates desta fase usam só classes Tailwind nativas (bg-blue-700, text-red-600) — sem tokens de marca (bg-brand, text-destructive) inexistentes no tailwind.config.js mínimo desta fase"

requirements-completed: [CORE-02, CFG-04]

# Metrics
duration: ~10min
completed: 2026-08-18
---

# Phase 1 Plan 4: Login/Logout — Views, Templates e Roteamento (Walking Skeleton completo) Summary

**Fatia vertical de login/logout via HTMX ligada ao `Usuario` real do PostgreSQL: `login_view`/`logout_view`/`shell_view`, `core/urls.py`, templates mínimas, e suíte de testes provando HTMX-redirect, CSRF round-trip, lockout do django-axes na 6ª tentativa e proteção contra open redirect — verificados também via `curl` real contra o container `web`.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-08-17
- **Completed:** 2026-08-18
- **Tasks:** 3 (2 `auto` + 1 `checkpoint:human-verify`, auto-aprovado em modo `--auto`)
- **Files modified:** 9 (7 criados, 2 modificados)

## Accomplishments
- `core/views.py` estendido com `login_view` (GET renderiza `core/login.html`; POST autentica via `authenticate(request, username=email, password=senha)`, nunca propaga `PermissionDenied`, distingue bloqueio via `request.axes_locked_out`), `logout_view` (`@require_POST`) e `shell_view` (protegida pelo `LoginRequiredMiddleware`) — `healthz` intocado
- Proteção contra open redirect: `?next=` só é aceito se `url_has_allowed_host_and_scheme(..., allowed_hosts={request.get_host()})` validar; caso contrário cai para `/`
- `core/urls.py` (`app_name="core"`, rotas `login/`, `logout/`, `""`) + `config/urls.py` com `include("core.urls")`
- Templates mínimas e funcionais: `login.html`, `_login_form.html` (CSRF lido do cookie via `htmx:configRequest`, nunca `hx-headers`), `shell.html` (saudação via `usuario_atual`, logout via `hx-post`)
- `core/tests/test_login_flow.py` (9 testes) e `core/tests/test_auth.py` (3 testes) — 12 testes cobrindo todos os casos do bloco `<behavior>` do plano
- Verificação de ponta a ponta via `docker compose up -d --build` + `curl` real contra o container `web` (superusuário `admin@sistemabase.local` reaproveitado do Plan 01-03): login HTMX com `HX-Redirect: /`, shell mostrando `Olá, admin@sistemabase.`, logout com `HX-Redirect: /login/`, raiz voltando a exigir login (302 → `/login/?next=/`), e 6ª tentativa de senha errada bloqueada permanecendo HTTP 200 com a mensagem de bloqueio — `axes_reset` rodado ao final para não deixar o admin bloqueado

## Task Commits

Each task was committed atomically:

1. **Task 1: Views de login/logout/shell + roteamento + testes de comportamento** - `0c4f407` (feat)
2. **Task 2: Templates de login (mínimas e funcionais) + shell autenticado** - `413d79e` (feat)
3. **Task 3: Login real via navegador (Walking Skeleton completo)** - checkpoint, sem diff de arquivo (ver seção "Checkpoint Task 3" abaixo)

**Plan metadata:** (a seguir, commit de documentação)

## Files Created/Modified
- `core/views.py` - `login_view`, `logout_view`, `shell_view` adicionadas (`healthz` mantida)
- `core/urls.py` - rotas `login/`, `logout/`, `""` sob `app_name="core"`
- `config/urls.py` - `include("core.urls")` adicionado ao final de `urlpatterns`
- `core/tests/__init__.py` - pacote de testes do app `core`
- `core/tests/test_login_flow.py` - 9 testes: GET/POST login, redirect da raiz, HTMX redirect, credenciais inválidas 200, lockout na 6ª tentativa, shell autenticado, logout, CSRF round-trip, open redirect
- `core/tests/test_auth.py` - 3 testes: `UsuarioManager.create_user`/`create_superuser`
- `core/templates/core/login.html` - tela de login (`{% extends "base.html" %}` + `{% include "core/_login_form.html" %}`)
- `core/templates/core/_login_form.html` - formulário HTMX (campos email/password, mensagens de erro/bloqueio, sem `hx-headers`)
- `core/templates/core/shell.html` - casca autenticada mínima (saudação + logout)

## Decisions Made
Nenhuma decisão de arquitetura nova — reprodução deliberada do padrão de login/logout/axes/CSRF já provado em produção na PCA (`core/views.py`, `core/urls.py`, `core/tests/test_login_flow.py`), generalizado e sem menção a domínio, conforme `CORE-02`/`CFG-04` e os Patterns 3/4 do `01-RESEARCH.md`. A única adição não presente literalmente na PCA é a validação explícita de `?next=` contra open redirect (T-04-03 do threat model desta plan), exigida pelo `must_haves` do plano.

## Deviations from Plan

None - plano executado exatamente como escrito.

## Issues Encountered

Na verificação manual via `curl` (evidência automatizada do checkpoint da Task 3), a primeira tentativa de simular as 5 tentativas erradas de senha retornou `403` (CSRF) porque o formulário enviado por `curl` não incluía o token CSRF — não é um bug de código, é a proteção `CsrfViewMiddleware` funcionando corretamente contra uma requisição sem token. Corrigido incluindo `X-CSRFToken` extraído do cookie na simulação; o comportamento de lockout foi então confirmado (6ª tentativa HTTP 200 com a mensagem de bloqueio). Nenhuma mudança de código foi necessária — o `Client` de teste do Django (usado nos 12 testes automatizados) já lida com isso automaticamente via `enforce_csrf_checks=False` por padrão.

## User Setup Required

None - nenhuma configuração de serviço externo necessária nesta plan. Para reproduzir a verificação manual localmente: `docker compose up -d --build`, depois `http://127.0.0.1:8000/login/` no navegador, logar com `admin@sistemabase.local` / `troque-esta-senha` (criado no Plan 01-03) ou outro superusuário local.

## Checkpoint Task 3 — Login real via navegador (Walking Skeleton completo)

**Modo `--auto` ativo** (`workflow.auto_advance=true`, `_auto_chain_active=true`) — checkpoint `type="checkpoint:human-verify"` com `gate="blocking"` (não `blocking-human`, portanto elegível para auto-aprovação). Evidência automatizada coletada substituindo a verificação manual no navegador:

1. `docker compose up -d --build` — `db` e `web` saudáveis (`docker compose ps` confirmado)
2. `curl -fsS http://127.0.0.1:8000/healthz` → `{"status": "ok"}` HTTP 200
3. `curl` GET `/login/` → HTTP 200 (equivalente à tela de login sem erro 500/404)
4. `curl` POST `/login/` com `HX-Request: true` + `X-CSRFToken` do cookie + credenciais do superusuário `admin@sistemabase.local` → HTTP 200 com header `HX-Redirect: /` (equivalente ao redirecionamento HTMX sem reload completo)
5. `curl` GET `/` com a sessão do passo anterior → HTTP 200, corpo contém `Olá, admin@sistemabase.` (saudação com e-mail do usuário logado)
6. `curl` POST `/logout/` com `HX-Request: true` → HTTP 200 com header `HX-Redirect: /login/`; `curl` GET `/` seguinte → HTTP 302 para `/login/?next=/` (login exigido de novo)
7. 5 tentativas de senha errada + 6ª tentativa via `curl` (com CSRF válido) → todas HTTP 200; a 6ª contém a mensagem de bloqueio ("Muitas tentativas de acesso...") — nunca a página genérica 403/429 do axes; `axes_reset` executado ao final para não deixar `admin@sistemabase.local` bloqueado após a verificação
8. Header `X-CSRFToken` confirmado presente e correto em toda requisição POST simulada (extraído do cookie `csrftoken` a cada chamada, nunca reaproveitado de um valor congelado) — prova equivalente à inspeção da aba Network do navegador

Suíte automatizada completa (`docker compose exec -T web python manage.py test core.tests -v 2`): **12/12 testes OK**, 0 falhas.

⚡ Checkpoint human-verify auto-aprovado (modo auto) — evidência automatizada registrada.

**Follow-up humano recomendado (não bloqueante):** confirmar visualmente no navegador real (abrir `http://127.0.0.1:8000/login/`, inspecionar a aba Network do DevTools) na próxima oportunidade de revisão humana — os 8 passos foram verificados via HTTP real (`curl`) e via `Client` de teste do Django, mas a inspeção visual do navegador em si (renderização CSS, foco de acessibilidade) não foi executada nesta sessão automatizada.

## Next Phase Readiness
- Walking Skeleton do Phase 1 completo: `docker compose up -d` sobe `db`+`web` saudáveis, um operador consegue logar com um usuário real do PostgreSQL, navegar na área autenticada mínima e deslogar — critério de sucesso 1 do `ROADMAP.md` fechado.
- `core/views.py`, `core/urls.py`, `config/urls.py` e as 3 templates estão prontos para o Phase 2 (`CORE-04`) estender com navegação/breadcrumbs/identidade visual completos sobre a mesma base de login/logout/shell.
- Nenhum bloqueio para o próximo plano/fase.

---
*Phase: 01-funda-o-django*
*Completed: 2026-08-18*
