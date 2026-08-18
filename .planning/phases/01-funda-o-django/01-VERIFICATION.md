---
phase: 01-funda-o-django
verified: 2026-08-18T00:45:00Z
status: passed
score: 5/5
verifier: inline (gsd-verifier não instalado neste runtime — verificação executada pelo orquestrador com sondas ao vivo)
requirements_checked: [CFG-01, CFG-02, CFG-03, CFG-04, CORE-01, CORE-02, INF-01, INF-02]
---

# Fase 1: Fundação Django — Verificação

**Status:** PASSED — 5/5 critérios de sucesso verificados contra o sistema vivo.

## Critérios de Sucesso (ROADMAP.md)

| # | Critério | Evidência | Status |
|---|----------|-----------|--------|
| 1 | `docker compose up -d` + `migrate` + `createsuperuser` sobe o sistema e permite login/logout | `docker compose ps`: db + web **healthy**; `/healthz` → HTTP 200; suíte de 13 testes cobre login (HX-Redirect), logout e shell autenticado; prova ao vivo via curl registrada em 01-04-SUMMARY.md | ✓ |
| 2 | `Usuario` customizado desde a migração 0001 | `core/migrations/0001_initial.py` cria `Usuario`; `core/models.py` tem `USERNAME_FIELD = "email"` + `UsuarioManager(use_in_migrations=True)`; `migrate --check` limpo | ✓ |
| 3 | Configuração sensível via `.env`; `.env.example` completo | `django-environ` em `config/settings/`; `.env.example` presente e cobrindo as variáveis usadas (critério de aceite do Plan 01-01) | ✓ |
| 4 | Invariantes de segurança e localização | Argon2 no topo de `PASSWORD_HASHERS`; django-axes com `AXES_LOCKOUT_CALLABLE` (HTTP 200 no bloqueio, testado); cookies `Secure`/`SameSite=Lax` (base.py:152–158); `SECURE_PROXY_SSL_HEADER` + HSTS + `DEBUG=False` + `ALLOWED_HOSTS` restrito (prod.py); `pt-br`/`America/Sao_Paulo`/`USE_TZ=True` | ✓ |
| 5 | CSRF do HTMX via `htmx:configRequest` lendo o cookie | Script em `core/templates/base.html`; `CSRF_COOKIE_HTTPONLY = False`; round-trip provado por teste (test_login_flow.py) | ✓ |

## Requisitos

| Requisito | Status | Evidência |
|-----------|--------|-----------|
| CFG-01 | Complete | settings por ambiente via django-environ (Plan 01-01) |
| CFG-02 | Complete | invariantes de segurança em base/prod (Plan 01-01 + fixes WR-02/WR-03/WR-04) |
| CFG-03 | Complete | localização pt-br/America-Sao_Paulo (Plan 01-01) |
| CFG-04 | Complete | htmx:configRequest + CSRF_COOKIE_HTTPONLY=False, teste round-trip (Plans 01-02/01-04) |
| CORE-01 | Complete | Usuario desde a 0001 (Plans 01-02/01-03) |
| CORE-02 | Complete | login/logout pela tela, 13 testes OK (Plan 01-04 + fix CR-01) |
| INF-01 | Complete | docker compose up com PostgreSQL 17, stack healthy (Plan 01-03) |
| INF-02 | Complete | .env.example completo (Plan 01-01) |

## Checagens adicionais

- **Zero menção a "PCA"** nos fontes rastreados (excluindo `.planning/` e `IDEIA.md`): confirmado por grep após o fix CR-02.
- **Code review**: 8 achados (2 críticos, 4 warnings, 2 info) — todos corrigidos (01-REVIEW-FIX.md), suíte re-executada: 13/13 OK.
- **Container não-root**: `whoami` no container → `app` (fix WR-01).
- **Bind seguro por padrão**: `${WEB_BIND_ADDRESS:-127.0.0.1}` no compose.yml (fix WR-02).

## Human verification (não bloqueante)

- Inspeção visual da tela de login num navegador real (DevTools: cookie CSRF, header X-CSRFToken) — o fluxo já está provado por teste e curl; a inspeção visual é refinamento estético, adiada para a Fase 2 (shell visual).
