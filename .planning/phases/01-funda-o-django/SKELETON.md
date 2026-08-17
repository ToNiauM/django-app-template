# Walking Skeleton — Sistema Base (Template CFC)

**Phase:** 1
**Generated:** 2026-08-17

## Capability Proven End-to-End

> "Um operador sobe `docker compose up -d`, roda `migrate` e `createsuperuser`, e um usuário real (armazenado no PostgreSQL, autenticado por e-mail) consegue logar e deslogar pela tela de login do sistema."

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Framework | Django 5.2.17 LTS, projeto "plano" na raiz (`manage.py`/`config/`/`core/`) | D-01 — parametrização Copier só na Fase 4; validar cada fase rodando o sistema de verdade |
| Data layer | PostgreSQL 17 (Docker, collation ICU pt-BR) via `psycopg[binary]` 3.3.4 + `django-environ` (`DATABASE_URL`) | CFG-01/CFG-03 — toda config sensível do `.env`; collation certa desde o 1º `initdb` (Pitfall 7, irreversível depois) |
| Auth | `Usuario` customizado (`AbstractUser`, sem `username`) + `UsuarioManager` próprio, `USERNAME_FIELD="email"`, desde a migração `0001` do app `core` | D-02/D-03 — invariante de SSO futuro; login por e-mail espelha a PCA |
| Segurança de sessão/login | Argon2 no topo de `PASSWORD_HASHERS`, `django-axes` (lockout usuário+IP, `AXES_USERNAME_FORM_FIELD="username"`, `AXES_LOCKOUT_CALLABLE`), cookies `Secure`/`SameSite=Lax`, `LoginRequiredMiddleware` (nega por padrão) | CFG-02 — invariantes de segurança da PCA, adaptadas ao `USERNAME_FIELD="email"` (Pitfalls 3/4/9) |
| CSRF + HTMX | `CSRF_COOKIE_HTTPONLY=False` + token lido do cookie a cada request via `htmx:configRequest` em `base.html` (nunca `hx-headers`) | CFG-04 — token sempre fresco, sobrevive a `rotate_token()` no login/logout (Pattern 4) |
| Deployment | Docker Compose: serviço `web` (Gunicorn, `python:3.12-slim`, `WEB_BIND_ADDRESS=127.0.0.1`) + serviço `db` (`postgres:17`), Tailwind compilado em estágio `node:20-alpine` descartável, `collectstatic` só no build (nunca no `entrypoint.sh`) | D-07/D-08/INF-01 — zero dependência do host além do Docker; app nunca exposto direto na rede |
| Diretório | `manage.py`, `config/settings/{base,dev,prod}.py`, `core/` (models, views, urls, templates, static, tests) na raiz — sem `apps/` ainda (chega na Fase 3) | Estrutura recomendada em `01-RESEARCH.md`; `core` fica agnóstico de domínio para a Fase 2 construir em cima |

## Stack Touched in Phase 1

- [x] Project scaffold (`manage.py`, `config/settings/{base,dev,prod}.py`, `requirements.txt`, `.env.example`)
- [x] Routing — `config/urls.py` (admin, healthz) + `core/urls.py` (login, logout, shell)
- [x] Database — `core.Usuario` criado via migração `0001` (write: `createsuperuser`; read: teste de login autenticando contra a linha gravada)
- [x] UI — tela de login HTMX (`core/templates/core/login.html` + `_login_form.html`) wired a `core.views.login_view`
- [x] Deployment — `docker compose up -d` sobe `web` + `db` localmente, com `healthz` respondendo 200

## Out of Scope (Deferred to Later Slices)

- Layout/shell completo com navegação e breadcrumbs, admin customizado com identidade visual, PWA (manifest/ícones/service worker), `django-simple-history` — tudo isso é **Fase 2** (`CORE-03..06`).
- CRUD de exemplo e dashboard ECharts — **Fase 3**.
- Parametrização Copier (`copier.yml`, variáveis de template, `copier update`) — **Fase 4**. Nesta fase o repositório é um projeto Django "plano" e executável (D-01).
- `ops/` (backup do banco, vhost nginx de exemplo), imagem Docker pinada em registry, volume Postgres `external` — **Fase 4** (`INF-03`). Nesta fase o volume `pgdata` é nomeado mas não `external`, para que `docker compose up -d` funcione sozinho no primeiro clone (ver `01-RESEARCH.md` Pitfall/Assumption A4).

## Subsequent Slice Plan

- Fase 2: shell visual completo (`base.html`/`shell.html` com navegação e breadcrumbs), admin customizado, PWA, `django-simple-history`.
- Fase 3: `apps/exemplo/` — CRUD de referência + dashboard ECharts.
- Fase 4: templatização Copier de tudo que foi construído nas Fases 1-3.
- Fase 5: verificação ponta a ponta do fluxo de nascimento + README.
