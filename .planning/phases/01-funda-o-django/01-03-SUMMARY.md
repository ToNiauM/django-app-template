---
phase: 01-funda-o-django
plan: 03
subsystem: infra
tags: [docker, docker-compose, postgresql-17, tailwindcss, gunicorn, whitenoise, migrations]

# Dependency graph
requires: ["01-01", "01-02"]
provides:
  - "Dockerfile multi-stage (node:20-alpine tailwind -> python:3.12-slim runtime) com collectstatic no build"
  - "entrypoint.sh (migrate --noinput + exec gunicorn, nunca collectstatic em runtime)"
  - "compose.yml com serviços web+db (postgres:17, collation ICU pt-BR, sem serviço backup, sem porta publicada no db)"
  - "tailwind.config.js mínimo (content apontando para core/templates)"
  - ".dockerignore"
  - "core/migrations/0001_initial.py — Usuario via UsuarioManager, sem HistoricalUsuario"
affects: ["01-04"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Migração do código para dentro da imagem só acontece em build (COPY . .) — qualquer arquivo gerado após o build (ex.: makemigrations via bind-mount pontual) exige rebuild antes de `up -d`, já que o serviço web não usa bind-mount de código em runtime"
    - "Guarda de tamanho do CSS do Tailwind (piso de 5000 bytes) falha o build cedo se o glob de `content` não casar com nenhum template"
    - "docker compose down sem -v preserva o volume nomeado pgdata — dados sobrevivem a restart mesmo sem `external: true` nesta fase"

key-files:
  created:
    - Dockerfile
    - compose.yml
    - entrypoint.sh
    - tailwind.config.js
    - .dockerignore
    - core/migrations/0001_initial.py
  modified:
    - config/settings/base.py

key-decisions:
  - "compose.yml com só web+db (sem backup — INF-03/Fase 4); volume pgdata nomeado sem external:true (Assumption A4 — clone limpo sobe sozinho com docker compose up -d)"
  - "Nome do projeto compose herdado do diretório (sistema_base), isolando containers/rede/volume de qualquer stack pca_* já rodando no mesmo host"

requirements-completed: [INF-01, INF-02]

# Metrics
duration: 15min
completed: 2026-08-17
---

# Phase 1 Plan 3: Infra Docker (Tailwind multi-stage + Postgres 17) + Migração 0001 Summary

**Dockerfile multi-stage (node:20-alpine compila Tailwind com guarda de 5000 bytes -> python:3.12-slim roda Gunicorn+WhiteNoise), compose.yml com Postgres 17 (collation ICU pt-BR, sem porta publicada) e a migração `0001` do app `core` — provado de ponta a ponta com `docker compose up -d`, `migrate`, `createsuperuser --noinput` e autenticação real via ORM no PostgreSQL.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-08-17T23:47:00Z (aprox.)
- **Completed:** 2026-08-18T00:01:58Z
- **Tasks:** 1
- **Files modified:** 7 (6 criados, 1 corrigido)

## Accomplishments
- `Dockerfile` multi-stage: estágio `assets` (`node:20-alpine`) compila `tailwindcss@3.4.17` com guarda de tamanho (falha se CSS < 5000 bytes — gerou 5122 bytes com o `content` apontando só para `core/templates`); estágio `runtime` (`python:3.12-slim`) instala `curl` (necessário pro healthcheck), instala dependências, copia o projeto, roda `collectstatic --noinput` com valores dummy de `SECRET_KEY`/`DATABASE_URL`
- `entrypoint.sh` roda só `migrate --noinput` + `exec gunicorn` — `collectstatic` nunca em runtime
- `compose.yml` com `db` (postgres:17, `POSTGRES_INITDB_ARGS` com `icu-locale=pt-BR`, sem `ports:`, healthcheck via `pg_isready`) e `web` (`depends_on: db: condition: service_healthy`, `ports: ["${WEB_BIND_ADDRESS}:${WEB_PORT}:8000"]`, healthcheck via `curl /healthz`, `start_period: 120s`) — sem serviço `backup` (fora de escopo desta fase)
- `core/migrations/0001_initial.py` gerada via `makemigrations core`: `CreateModel` de `Usuario` com manager `core.models.UsuarioManager`, sem `HistoricalUsuario`
- Sequência real de verificação executada de ponta a ponta neste host (compartilhado com a stack de produção da PCA, isolado por nome de projeto `sistema_base` — sem colisão de container/rede/volume com `pca_*`):
  1. `docker compose build web` — CSS 5122 bytes, `collectstatic` copiou 170 arquivos
  2. `docker compose run --rm -v "$PWD:/app" --entrypoint python web manage.py makemigrations core` — gerou a migração no host
  3. `docker compose up -d` — `db` e `web` saudáveis (`db` ~25s, `web` ~40s de `start_period`)
  4. `curl -fsS http://127.0.0.1:8000/healthz` → `{"status": "ok"}` HTTP 200
  5. `psql -c "\d core_usuario"` confirma coluna `email` com `UNIQUE CONSTRAINT`
  6. `createsuperuser --noinput` (email `admin@sistemabase.local`) → `Superuser created successfully.`
  7. `manage.py shell` via ORM: `u.is_superuser` e `u.check_password(...)` → `True True`
  8. `migrate --check` → sem migrações pendentes (exit 0)

## Task Commits

Each task was committed atomically:

1. **Task 1: Docker infra + gerar migração 0001 + subir o sistema (walking skeleton)** - `8282bdc` (feat)

**Plan metadata:** (a seguir, commit de documentação)

## Files Created/Modified
- `Dockerfile` - build multi-stage (assets Tailwind -> runtime Python), guarda de 5000 bytes, `collectstatic` no build
- `compose.yml` - serviços `db` (postgres:17, ICU pt-BR, sem porta publicada) e `web` (healthcheck `/healthz`, porta só via `WEB_BIND_ADDRESS`)
- `entrypoint.sh` - `migrate --noinput` + `exec gunicorn`
- `tailwind.config.js` - `content: ["./core/templates/**/*.html"]`, sem paleta de marca (fora de escopo)
- `.dockerignore` - `.git`, `.env`, caches, `staticfiles/`, `core/static/dist/`, `.planning/`, `*.md`
- `core/migrations/0001_initial.py` - `CreateModel` de `Usuario`, manager `UsuarioManager`, sem `HistoricalUsuario`
- `config/settings/base.py` - remoção de entrada duplicada `"core"` em `INSTALLED_APPS` (bug herdado do Plan 01-01, ver Deviations)

## Decisions Made
- `compose.yml` restrito a `web`+`db` — sem `backup` (`INF-03`, escopo da Fase 4) e sem `external: true` no volume `pgdata` (Assumption A4: um clone novo precisa subir sozinho com `docker compose up -d`, sem `docker volume create` manual). Reavaliar `external:true` quando este template gerar um sistema real de produção.
- Nome de projeto do compose herdado do nome do diretório (`sistema_base`) — isola containers, rede e volume de qualquer stack `pca_*` já em execução no mesmo host (verificado: `docker ps`/`docker network ls` não mostraram nenhuma colisão de nome antes ou depois da subida).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking issue] `INSTALLED_APPS` com `core` duplicado impedia `collectstatic`**
- **Found during:** Task 1, primeiro `docker compose build web`
- **Issue:** `config/settings/base.py` (Plan 01-01) listava tanto `"core.apps.CoreConfig"` quanto `"core"` em `INSTALLED_APPS`, causando `django.core.exceptions.ImproperlyConfigured: Application labels aren't unique, duplicates: core` no `collectstatic` do build da imagem.
- **Fix:** Removida a entrada redundante `"core"`, mantendo só `"core.apps.CoreConfig"`.
- **Files modified:** `config/settings/base.py`
- **Verification:** `docker compose build web` completou com `collectstatic` copiando 170 arquivos; `docker compose exec web python manage.py migrate --check` retornou sem pendências.
- **Committed in:** `8282bdc` (parte do commit da Task 1)

**2. [Rule 1 - Bug de auditoria] Comentário do Dockerfile continha a string literal `COPY apps`, violando o critério de aceite de zero ocorrências**
- **Found during:** Task 1 (verificação dos critérios de aceite)
- **Issue:** O comentário explicando por que não existe instrução de cópia do diretório `apps/` citava literalmente a substring `COPY apps`, o que o grep de auditoria do plano proíbe (`grep -q 'COPY apps' Dockerfile` deve retornar 0 ocorrências).
- **Fix:** Reescrito o comentário para explicar o mesmo motivo sem citar a string proibida.
- **Files modified:** `Dockerfile`
- **Verification:** `grep -c 'COPY apps' Dockerfile` retorna 0; build refeito com sucesso (imagem reconstruída, `web`/`db` saudáveis, `/healthz` 200).
- **Committed in:** `8282bdc` (parte do commit da Task 1, aplicado antes do commit)

**3. [Rule 1 - Bug de sequência] Imagem `web` construída antes da migração existir não continha `0001_initial.py`, causando crash-loop no `migrate`**
- **Found during:** Task 1, primeiro `docker compose up -d`
- **Issue:** O serviço `web` não usa bind-mount de código em runtime — `COPY . .` acontece só em build. A sequência do plano builda a imagem (passo 2) e só depois gera a migração via bind-mount pontual (passo 3); sem um rebuild entre os passos 3 e 4, a imagem usada por `up -d` não contém `core/migrations/0001_initial.py`, e `entrypoint.sh` falhava com `ValueError: Dependency on app with no migrations: core`, reiniciando em loop.
- **Fix:** Adicionado um `docker compose build web` (rebuild) imediatamente após o `makemigrations` e antes do `up -d` — necessário sempre que a migração `0001` (ou qualquer código) for gerada/alterada depois do build da imagem.
- **Files modified:** nenhum arquivo de código; passo operacional adicionado à sequência de verificação.
- **Verification:** Após o rebuild, `docker compose up -d` subiu `db`+`web` saudáveis em ~40s; `migrate --check` sem pendências.
- **Committed in:** não aplicável (passo de verificação, não gera diff de arquivo)

---

**Total deviations:** 3 auto-fixed (1 bug bloqueante herdado do Plan 01-01, 1 bug de auditoria/lint, 1 ajuste de sequência operacional)
**Impact on plan:** Nenhuma mudança de escopo ou arquitetura. A correção em `config/settings/base.py` era necessária para o `collectstatic` funcionar — sem ela, esta plan não teria como provar o build. O ajuste de sequência (rebuild após `makemigrations`) é documentado aqui para quem reproduzir os passos de verificação do plano literalmente.

## Issues Encountered
- Arquivo `core/migrations/0001_initial.py`, gerado dentro do container via bind-mount, saiu com owner `root:root` no host — corrigido com `chown` antes do `git add` (nenhum problema de conteúdo, só de permissão do processo do container rodando como root).
- `collectstatic` emite avisos ("Found another file with the destination path...") porque `STATICFILES_DIRS` (`core/static`) e o finder de app do próprio `core` apontam para o mesmo diretório — duplicação inofensiva herdada do Plan 01-01/01-02, fora do escopo desta plan (não bloqueia nada, não afeta o resultado final do `collectstatic`).
- `IDEIA.md` (arquivo pré-existente, não rastreado, criado fora do fluxo GSD antes desta sessão) contém menções a "PCA" — está fora do escopo desta plan (não foi criado nem modificado por ela) e não foi tocado.

## User Setup Required

Nenhuma configuração de serviço externo. Para reproduzir localmente: copiar `.env.example` para `.env`, preencher `SECRET_KEY` (`python3 -c "import secrets; print(secrets.token_urlsafe(50))"`) e `POSTGRES_PASSWORD`, depois `docker compose build web && docker compose up -d`.

## Next Phase Readiness
- Walking skeleton completo: `docker compose up -d` sobe `db`+`web` saudáveis a partir de um clone limpo (só preenchendo `.env`, sem `docker volume create`); `migrate` cria a tabela do `Usuario`; um superusuário real foi criado e autenticado via ORM no PostgreSQL.
- `core/views.py` e `config/urls.py` seguem prontos para o Plan 01-04 estender com `login_view`/`logout_view`/`shell_view` e `core/urls.py`/`include("core.urls")` — nenhuma mudança nesta plan nesses arquivos.
- Nenhum bloqueio para o Plan 01-04.

---
*Phase: 01-funda-o-django*
*Completed: 2026-08-17*

## Self-Check: PASSED

All 6 created files verified present on disk (Dockerfile, compose.yml, entrypoint.sh, tailwind.config.js, .dockerignore, core/migrations/0001_initial.py); task commit (`8282bdc`) verified in `git log`.
