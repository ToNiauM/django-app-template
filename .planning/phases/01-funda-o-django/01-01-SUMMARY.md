---
phase: 01-funda-o-django
plan: 01
subsystem: infra
tags: [django, django-environ, django-axes, argon2, whitenoise, gunicorn, postgres, settings]

# Dependency graph
requires: []
provides:
  - "manage.py e config/wsgi.py executáveis (DJANGO_SETTINGS_MODULE=config.settings.dev por padrão)"
  - "config/settings/base.py com INSTALLED_APPS, MIDDLEWARE (ordem normativa), AUTH_USER_MODEL=core.Usuario, PASSWORD_HASHERS (Argon2 no topo), AUTHENTICATION_BACKENDS + AXES_*, TEMPLATES com context_processors, DATABASES via django-environ, localização pt-br/America-Sao_Paulo, STORAGES, cookies CSRF/sessão seguros"
  - "config/settings/dev.py e config/settings/prod.py (DEBUG=False, ALLOWED_HOSTS restrito, SECURE_PROXY_SSL_HEADER, HSTS, SECURE_REDIRECT_EXEMPT para healthz, AXES_IPWARE_*)"
  - "requirements.txt fixando as 9 dependências desta fase"
  - ".env.example cobrindo 100% das variáveis usadas"
  - ".gitignore cobrindo .env, caches, staticfiles, sqlite, venv"
affects: [01-02-core-kernel, 01-03-infra-docker, 01-04]

# Tech tracking
tech-stack:
  added: [Django==5.2.17, "psycopg[binary]==3.3.4", django-environ==0.14.0, django-axes==8.3.1, django-htmx==1.29.0, argon2-cffi==25.1.0, whitenoise==6.12.0, gunicorn==26.0.0, django-ipware==7.0.1]
  patterns:
    - "Settings por ambiente: base.py comum + dev.py/prod.py fazem `from .base import *` e sobrescrevem só o que diverge"
    - "Toda configuração sensível vem do .env via django-environ (env.db, env.list, env.bool, env.int) — nunca os.environ.get espalhado"
    - "STORAGES (dict) em vez de STATICFILES_STORAGE (removido no Django 5.1)"
    - "AXES_USERNAME_FORM_FIELD='username' explícito — Django sempre usa o kwarg literal username= em authenticate(), mesmo com USERNAME_FIELD='email'"
    - "AXES_LOCKOUT_CALLABLE aponta para um módulo que ainda não existe (core.axes_lockout) — resolvido no Plan 01-02, intencional"

key-files:
  created:
    - manage.py
    - config/__init__.py
    - config/wsgi.py
    - config/settings/__init__.py
    - config/settings/base.py
    - config/settings/dev.py
    - config/settings/prod.py
    - requirements.txt
    - .env.example
    - .gitignore
  modified: []

key-decisions:
  - "Reproduzida literalmente a topologia de settings/middleware/axes/CSRF da PCA (fonte de extração em produção), generalizada e sem menção a domínio"
  - "requirements.txt restrito às 9 dependências desta fase — sem django-simple-history (Fase 2) e sem openpyxl/freezegun (fora de escopo)"
  - "STORAGES sempre como dict (nunca STATICFILES_STORAGE, removido no Django 5.1) — inclusive nos comentários explicativos, para não falhar o grep de auditoria"

patterns-established:
  - "Settings por ambiente com django-environ: base/dev/prod"
  - "AUTH_USER_MODEL='core.Usuario' declarado desde já — módulo core ainda não existe, é resolvido no Plan 01-02"
  - "CSRF_COOKIE_HTTPONLY=False é invariante do projeto (não bug) — HTMX lê o cookie a cada requisição via htmx:configRequest, implementado no Plan 01-02"

requirements-completed: [CFG-01, CFG-02, CFG-03]

# Metrics
duration: 6min
completed: 2026-08-17
---

# Phase 1 Plan 1: Scaffold Django + Settings por Ambiente Summary

**Scaffold Django 5.2 "plano" (manage.py, config/wsgi.py) com settings por ambiente (base/dev/prod) via django-environ, aplicando Argon2, django-axes, cookies seguros, HSTS/proxy e localização pt-br/America-Sao_Paulo desde já — requirements.txt fixa as 9 dependências e .env.example cobre 100% das variáveis.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-08-17T23:47:56Z
- **Completed:** 2026-08-17T23:54:00Z
- **Tasks:** 1
- **Files modified:** 10

## Accomplishments
- `config/settings/base.py` com toda a topologia normativa de MIDDLEWARE, AUTHENTICATION_BACKENDS, AXES_*, TEMPLATES (context_processors incluindo `core.context_processors.usuario_atual`) e localização pt-br
- `config/settings/prod.py` com todas as invariantes de segurança de produção (DEBUG=False, ALLOWED_HOSTS restrito, SECURE_PROXY_SSL_HEADER, SECURE_REDIRECT_EXEMPT para o healthz, HSTS, AXES_IPWARE_*)
- `requirements.txt` fixando exatamente as 9 dependências auditadas na pesquisa (todas `[OK]` no slopcheck)
- `.env.example` documentando 100% das variáveis usadas, com comentários em pt-BR e "Sistema Base" como placeholder neutro

## Task Commits

Each task was committed atomically:

1. **Task 1: Scaffold Django + settings por ambiente** - `cd9eb62` (feat)

**Plan metadata:** (a seguir, commit de documentação)

## Files Created/Modified
- `manage.py` - entrypoint de gerência Django, default `config.settings.dev`
- `config/__init__.py` - pacote `config`
- `config/wsgi.py` - aplicação WSGI, default `config.settings.dev`
- `config/settings/__init__.py` - pacote `config.settings`
- `config/settings/base.py` - settings comuns: apps, middleware, AUTH_USER_MODEL, axes, hashers, templates, database, localização, storages, cookies
- `config/settings/dev.py` - `DEBUG` via env, `ALLOWED_HOSTS=["*"]`, storage sem manifest, `WHITENOISE_USE_FINDERS`
- `config/settings/prod.py` - `DEBUG=False`, `ALLOWED_HOSTS` restrito, proxy/HSTS, `SECURE_REDIRECT_EXEMPT`, `AXES_IPWARE_*`
- `requirements.txt` - 9 dependências pinadas
- `.env.example` - todas as variáveis usadas em base/dev/prod, comentadas em pt-BR
- `.gitignore` - `.env`, caches, staticfiles, sqlite, venv, logs

## Decisions Made
- Nenhuma decisão de arquitetura nova nesta plan — reprodução deliberada da topologia já provada em produção na PCA (settings/middleware/axes/CSRF), generalizada e sem menção a domínio, conforme D-05/D-06/CFG-01/CFG-02/CFG-03 do CONTEXT.md e RESEARCH.md desta fase.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Comentário explicativo mencionava literalmente `STATICFILES_STORAGE`, violando o critério de aceite de zero ocorrências**
- **Found during:** Task 1 (verificação dos critérios de aceite)
- **Issue:** O comentário em `config/settings/base.py` explicando por que se usa o dict `STORAGES` citava o nome literal da chave removida (`STATICFILES_STORAGE`), o que o `grep` de auditoria do plano proíbe explicitamente (`grep -q 'STATICFILES_STORAGE' config/settings/base.py` deve retornar 0 ocorrências).
- **Fix:** Reescrito o comentário para explicar o mesmo motivo sem citar a string literal proibida.
- **Files modified:** `config/settings/base.py`
- **Verification:** `grep -c STATICFILES_STORAGE config/settings/base.py` retorna 0; demais critérios de aceite continuam passando.
- **Committed in:** `cd9eb62` (parte do commit da Task 1, aplicado antes do commit)

---

**Total deviations:** 1 auto-fixed (1 bug de auditoria/lint)
**Impact on plan:** Correção trivial de texto de comentário, sem impacto funcional. Nenhum scope creep.

## Issues Encountered
None.

## User Setup Required

None - nenhuma configuração de serviço externo necessária nesta plan. `.env` real (com segredos) deve ser criado a partir de `.env.example` antes de rodar o Django de ponta a ponta — isso acontece no Plan 01-03 (infra Docker), não nesta plan.

## Next Phase Readiness
- `config/settings/base.py` já referencia `core.apps.CoreConfig`, `core.middleware.HtmxRedirectMiddleware`, `core.axes_lockout.resposta_bloqueio` e `core.context_processors.usuario_atual` — módulos que o Plan 01-02 (app `core`: `Usuario`, axes callable, middleware, kernel HTMX) cria em seguida.
- Django ainda não sobe de ponta a ponta nesta plan (falta o app `core` — Plan 01-02 — e a infraestrutura Docker — Plan 01-03); isso é esperado e documentado no objetivo do plano.
- Nenhum bloqueio para o Plan 01-02.

---
*Phase: 01-funda-o-django*
*Completed: 2026-08-17*

## Self-Check: PASSED

All 10 created files verified present on disk; both task commits (`cd9eb62`, `6b6003b`) verified in `git log`.
