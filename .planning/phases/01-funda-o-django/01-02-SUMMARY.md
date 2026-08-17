---
phase: 01-funda-o-django
plan: 02
subsystem: core
tags: [django, custom-user, django-axes, htmx, csrf, middleware, healthz]

# Dependency graph
requires: ["01-01"]
provides:
  - "core.Usuario (AbstractUser) + UsuarioManager com use_in_migrations=True, login por e-mail (USERNAME_FIELD=email)"
  - "core.apps.CoreConfig (default_auto_field=BigAutoField, name=core)"
  - "core.axes_lockout.resposta_bloqueio referenciado por AXES_LOCKOUT_CALLABLE"
  - "core.middleware.HtmxRedirectMiddleware (converte 301/302 em HX-Redirect quando request.htmx)"
  - "core.context_processors.usuario_atual (expõe o usuário autenticado ao template)"
  - "core.views.healthz (SELECT 1, JsonResponse ok/error 503)"
  - "config/urls.py com admin/ e healthz"
  - "core/templates/base.html com o script htmx:configRequest lendo o cookie csrftoken"
  - "assets vendorizados: core/static/vendor/htmx.min.js (1.9.12) e alpine.min.js (3.16.2)"
  - "core/static/src/input.css (diretivas Tailwind puras)"
  - "core/README.md documentando 3 convenções não-óbvias do kernel"
affects: [01-03-infra-docker, 01-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Usuario customizado (AbstractUser) presente desde antes da migração 0001, com manager próprio use_in_migrations=True — nunca troca depois de migrado (D-03)"
    - "AXES_LOCKOUT_CALLABLE aponta para um callable que preserva a resposta 200 original da view, nunca a página genérica do axes"
    - "Redirects em views acessadas via HTMX sempre via django_htmx.http.HttpResponseClientRedirect + HtmxRedirectMiddleware central para o caso genérico (nunca redirect() puro)"
    - "CSRF do HTMX lido do cookie csrftoken a cada requisição via htmx:configRequest, nunca hx-headers estático (token rotaciona no login/logout)"
    - "Assets de terceiros (htmx/Alpine) vendorizados e commitados no repo, nunca carregados via CDN em runtime (offline-first)"

key-files:
  created:
    - core/__init__.py
    - core/apps.py
    - core/models.py
    - core/migrations/__init__.py
    - core/axes_lockout.py
    - core/middleware.py
    - core/context_processors.py
    - core/views.py
    - config/urls.py
    - core/templates/base.html
    - core/static/src/input.css
    - core/static/vendor/htmx.min.js
    - core/static/vendor/alpine.min.js
    - core/README.md
  modified: []

key-decisions:
  - "Reproduzido verbatim o padrão Usuario/UsuarioManager/axes_lockout/middleware/context_processor da PCA (fonte de extração em produção), sem nada de domínio"
  - "core/apps.py criado só com CoreConfig — sem PcaAdminConfig/default_site, que é CORE-03 (Fase 2); django.contrib.admin usa o AdminSite padrão do Django nesta fase"
  - "core/views.py criado só com healthz — login_view/logout_view/shell_view ficam para o Plan 01-04, que estende este arquivo"
  - "config/urls.py criado só com admin+healthz — sem include('core.urls'), que ainda não existe até o Plan 01-04 criá-lo"

requirements-completed: [CORE-01, CFG-04]

# Metrics
duration: 8min
completed: 2026-08-17
---

# Phase 1 Plan 2: Core Kernel — Usuario, axes, middleware, htmx CSRF, healthz Summary

**Kernel do app `core`: `Usuario` customizado com login por e-mail (`UsuarioManager`, `USERNAME_FIELD="email"`), callable de lockout do django-axes que preserva a resposta 200 da view, `HtmxRedirectMiddleware`, context processor, `healthz`, e `base.html` com o script `htmx:configRequest` que lê o token CSRF do cookie a cada requisição.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-08-17
- **Completed:** 2026-08-17
- **Tasks:** 1
- **Files modified:** 14

## Accomplishments
- `core/models.py` com `Usuario(AbstractUser)` + `UsuarioManager` — login por e-mail, `USERNAME_FIELD="email"`, `use_in_migrations=True`, mensagens de erro em pt-BR, pronto para a migração `0001` do Plan 01-03
- `core/axes_lockout.py` com `resposta_bloqueio` referenciado por `AXES_LOCKOUT_CALLABLE` (Plan 01-01), preservando a resposta 200 original da view em vez da página genérica do axes
- `core/middleware.py` com `HtmxRedirectMiddleware` convertendo 301/302 em `HX-Redirect` para requisições HTMX
- `core/context_processors.py` e `core/views.py` (só `healthz`, decorado com `@login_not_required`, `SELECT 1` via `connection.cursor()`)
- `config/urls.py` com `admin/` e `healthz`
- `core/templates/base.html` com o script `htmx:configRequest` (lê `csrftoken` do cookie via regex, seta `X-CSRFToken` a cada requisição — nunca `hx-headers` estático)
- Assets vendorizados: `htmx.min.js` (1.9.12, 48101 bytes) e `alpine.min.js` (3.16.2, 54447 bytes), baixados de `unpkg.com` e commitados no repo
- `core/static/src/input.css` com as 3 diretivas Tailwind puras
- `core/README.md` documentando 3 convenções não-óbvias: `timezone.localdate()` para "hoje", `AXES_USERNAME_FORM_FIELD="username"` proposital, `AUTH_USER_MODEL` imutável após `0001`

## Task Commits

Each task was committed atomically:

1. **Task 1: Core kernel — Usuario, axes, middleware, htmx CSRF, healthz** - `3b1d19e` (feat)

**Plan metadata:** (a seguir, commit de documentação)

## Files Created/Modified
- `core/__init__.py` - pacote `core`
- `core/apps.py` - `CoreConfig` (sem `PcaAdminConfig`/`default_site` — isso é `CORE-03`, Fase 2)
- `core/models.py` - `Usuario`/`UsuarioManager`, login por e-mail
- `core/migrations/__init__.py` - pacote de migrações do app `core` (sem migração gerada ainda — Plan 01-03)
- `core/axes_lockout.py` - `resposta_bloqueio`, callable do `AXES_LOCKOUT_CALLABLE`
- `core/middleware.py` - `HtmxRedirectMiddleware`
- `core/context_processors.py` - `usuario_atual`
- `core/views.py` - só `healthz` (login/logout/shell é Plan 01-04)
- `config/urls.py` - `admin/` + `healthz` (sem `include("core.urls")` ainda)
- `core/templates/base.html` - HTML5 mínimo + script `htmx:configRequest`
- `core/static/src/input.css` - 3 diretivas Tailwind
- `core/static/vendor/htmx.min.js` - htmx 1.9.12 vendorizado
- `core/static/vendor/alpine.min.js` - Alpine 3.16.2 vendorizado
- `core/README.md` - 3 convenções não-óbvias do kernel

## Decisions Made
Nenhuma decisão de arquitetura nova nesta plan — reprodução deliberada do kernel `core` já provado em produção na PCA (Usuario/axes/middleware/context processor/CSRF via `htmx:configRequest`), generalizado e sem menção a domínio, conforme `CORE-01`/`CFG-04` e os Patterns 2/4 e Pitfalls 3/4/8/9 do `01-RESEARCH.md`.

## Deviations from Plan

None - plano executado exatamente como escrito.

## Issues Encountered
None.

## User Setup Required

None - nenhuma configuração de serviço externo necessária nesta plan.

## Next Phase Readiness
- O app `core` referenciado desde o Plan 01-01 (`INSTALLED_APPS`, `MIDDLEWARE`, `AUTHENTICATION_BACKENDS`, `TEMPLATES.context_processors`) agora existe de fato com todos os módulos que essas configurações apontam.
- `core.Usuario` está pronto para a migração `0001` (Plan 01-03, que também sobe Docker+Postgres real).
- `core/views.py` e `config/urls.py` estão prontos para o Plan 01-04 estender com `login_view`/`logout_view`/`shell_view` e `core/urls.py`/`include("core.urls")`.
- Django ainda não roda de ponta a ponta nesta plan (falta infraestrutura Docker+Postgres — Plan 01-03; ambiente local não tem Django instalado para rodar `manage.py check`, verificação feita via `py_compile` + greps de critérios de aceite); isso é esperado e documentado no objetivo do plano.
- Nenhum bloqueio para o Plan 01-03.

---
*Phase: 01-funda-o-django*
*Completed: 2026-08-17*

## Self-Check: PASSED

All 14 created files verified present on disk (core/__init__.py, core/apps.py, core/models.py, core/migrations/__init__.py, core/axes_lockout.py, core/middleware.py, core/context_processors.py, core/views.py, config/urls.py, core/templates/base.html, core/static/src/input.css, core/static/vendor/htmx.min.js, core/static/vendor/alpine.min.js, core/README.md); task commit (`3b1d19e`) verified in `git log`.
