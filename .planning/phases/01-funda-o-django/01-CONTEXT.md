# Phase 1: Fundação Django - Context

**Gathered:** 2026-08-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Um projeto Django 5.2 rodando em Docker Compose (app + PostgreSQL 17), com `Usuario` customizado desde a primeira migração, login/logout funcionais e settings por ambiente que aplicam as invariantes de segurança e localização da PCA. Nesta fase o repositório é um **sistema-modelo executável** (não ainda um template Copier — a templatização é a Fase 4).

Requisitos cobertos: CFG-01, CFG-02, CFG-03, CFG-04, CORE-01, CORE-02, INF-01, INF-02.

</domain>

<decisions>
## Implementation Decisions

*(Modo `--auto`: decisões selecionadas automaticamente com a opção recomendada, ancoradas na PCA — fonte de extração declarada em PROJECT.md.)*

### Estratégia de desenvolvimento
- **D-01:** O repositório é desenvolvido como projeto Django "plano" e executável na raiz (`manage.py`, `config/`, `core/`, `apps/`). A parametrização Copier (jinja, `copier.yml`) só entra na Fase 4. Motivo: permite validar cada fase rodando o sistema de verdade, e a templatização é uma transformação mecânica no final.

### Autenticação
- **D-02:** Login por **e-mail** — `USERNAME_FIELD = "email"`, sem campo `username`. Espelha a PCA (`/opt/web/pca/core/models.py`): `UsuarioManager(BaseUserManager)` com `use_in_migrations = True`, `create_user`/`create_superuser` recebendo `email` como primeiro argumento posicional.
- **D-03:** `AUTH_USER_MODEL = "core.Usuario"` definido desde a migração 0001 do `core` (invariante para não inviabilizar SSO futuro).
- **D-04:** `django-axes` configurado com lockout customizado (a PCA tem `core/axes_lockout.py` e nota em `base.py` sobre `USERNAME_FIELD="email"` — replicar o padrão).

### Settings e configuração
- **D-05:** Settings em módulos por ambiente: `config/settings/base.py` + `dev.py` + `prod.py`, selecionados por `DJANGO_SETTINGS_MODULE`, com `django-environ` lendo tudo do `.env`. Espelha a PCA.
- **D-06:** Dependências via `requirements.txt` (padrão da PCA; sem poetry/uv/pyproject nesta fase).

### Docker e assets
- **D-07:** Tailwind compilado em **estágio multi-stage do Dockerfile** (`node:20-alpine` rodando `npx tailwindcss@3.4.17 --minify`), com guarda de tamanho do CSS gerado (falha o build se só o preflight for emitido — padrão comentado no Dockerfile da PCA). Nenhuma dependência de node no host.
- **D-08:** Runtime `python:3.12-slim`, Gunicorn atrás do proxy, app escutando só em `127.0.0.1` no host (publicação de porta restrita), WhiteNoise para estáticos.

### Claude's Discretion
- Detalhes de `compose.yml`, `entrypoint.sh` e healthchecks: extrair o padrão da PCA e generalizar (remover qualquer menção a PCA/domínio).
- Estrutura exata da tela de login desta fase: mínima e funcional; a identidade visual completa (shell, navegação) é a Fase 2.
- Versões exatas de dependências: partir do `requirements.txt` da PCA, atualizando patches quando seguro.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Fonte de extração (somente leitura — NUNCA modificar)
- `/opt/web/pca/` — sistema em produção do qual o template é extraído. Em particular:
  - `/opt/web/pca/config/settings/base.py`, `dev.py`, `prod.py` — padrão de settings, segurança, axes, localização
  - `/opt/web/pca/core/models.py` — `Usuario` + `UsuarioManager` (login por e-mail)
  - `/opt/web/pca/core/axes_lockout.py`, `middleware.py`, `context_processors.py` — kernel replicável
  - `/opt/web/pca/Dockerfile`, `compose.yml`, `entrypoint.sh`, `requirements.txt`, `tailwind.config.js` — infra replicável
  - `/opt/web/pca/ops/` — backup e vhost nginx de exemplo

### Documentos do projeto
- `IDEIA.md` — visão, decisões fechadas, invariantes herdadas da PCA, critérios de sucesso
- `.planning/PROJECT.md` — contexto e restrições consolidados (stack fechada, fora de escopo)
- `.planning/REQUIREMENTS.md` — requisitos v1 com REQ-IDs (esta fase: CFG-01..04, CORE-01, CORE-02, INF-01, INF-02)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Repositório atual está vazio (greenfield) — só `IDEIA.md` e `.planning/`.
- A PCA (`/opt/web/pca`) contém todos os padrões a extrair e generalizar; ela já separa boilerplate (`config/`, `core/`, infra) de domínio (`apps/`).

### Established Patterns
- Settings por ambiente com comentários explicativos em pt-BR (estilo da casa: comentários que explicam o *porquê*).
- Dockerfile multi-stage com validação do CSS do Tailwind embutida no build.
- CSRF do HTMX via `htmx:configRequest` lendo o token do cookie (`CSRF_COOKIE_HTTPONLY = False`) — nunca `hx-headers`.

### Integration Points
- Fase 2 (Shell Visual) construirá sobre o `core` criado aqui; manter `core` agnóstico de domínio.
- Fase 4 (Copier) transformará os valores desta fase (nome, slug, porta, banco, cor) em variáveis — evitar espalhar esses valores; concentrá-los em settings/`.env`.

</code_context>

<specifics>
## Specific Ideas

- Zero menção a "PCA" ou a qualquer domínio no código novo — usar nomes neutros ("Sistema Base" como placeholder que virará variável Copier).
- Critério de sucesso operacional: `docker compose up -d` + `migrate` + `createsuperuser` → sistema navegável com login.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope (modo auto, sem novas capacidades sugeridas).

</deferred>

---

*Phase: 1-Fundação Django*
*Context gathered: 2026-08-17*
