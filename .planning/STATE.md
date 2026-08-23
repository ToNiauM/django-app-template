---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: executing
stopped_at: Completed 07-01-PLAN.md
last_updated: "2026-08-23T17:53:20.739Z"
last_activity: 2026-08-23
progress:
  total_phases: 7
  completed_phases: 6
  total_plans: 32
  completed_plans: 25
  percent: 78
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-17)

**Core value:** Criar um sistema novo funcional (login, layout, CRUD de exemplo, dashboard de exemplo, Docker, backup) em minutos — restando ao time apenas modelar o domínio em `apps/`.
**Current focus:** Phase 07 — herdar-o-design-system-do-pca

## Current Position

Phase: 07 (herdar-o-design-system-do-pca) — EXECUTING
Plan: 2 of 8
Status: Ready to execute
Last activity: 2026-08-23

Progress: [████████░░] 78%

## Performance Metrics

**Velocity:**

- Total plans completed: 21
- Average duration: -
- Total execution time: -

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 4 | - | - |
| 2 | 4 | - | - |
| 04 | 7 | - | - |
| 05 | 3 | - | - |
| 06 | 3 | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
| Phase 01 P01 | 6min | 1 tasks | 10 files |
| Phase 01-funda-o-django P02 | 8min | 1 tasks | 14 files |
| Phase 01-funda-o-django P03 | 15min | 1 tasks | 6 files |
| Phase 01-funda-o-django P04 | 10min | 3 tasks | 9 files |
| Phase 02 P01 | 4min | 2 tasks | 6 files |
| Phase 02 P02 | 5min | 3 tasks | 7 files |
| Phase 02 P03 | 6min | 3 tasks | 10 files |
| Phase 02 P04 | 5min | 3 tasks | 10 files |
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 05 P01 | 196min | 1 tasks | 5 files |
| Phase 06 P01 | 8min | 3 tasks | 8 files |
| Phase 06 P02 | 9min | 3 tasks | 6 files |
| Phase 06 P03 | 4min | 3 tasks | 4 files |
| Phase 07 P01 | 18min | 3 tasks | 5 files |

## Accumulated Context

### Roadmap Evolution

- Phase 6 added
- Phase 7 added (2026-08-23): Herdar o design system do PCA — o padrão visual do Sistema CFC passa a nascer com todo sistema gerado. Pedido do operador.
  - **Rota decidida**: o template herda **direto de `/opt/web/pca`**, não do DividaAtiva. Motivo: o PCA é anterior ao template (não tem `.copier-answers.yml`) e é a fonte real do padrão; o DividaAtiva tem só um recorte dele. Herdar do filho implicaria implementar o mesmo sistema duas vezes e conflitar com o próprio trabalho do filho no `copier update` seguinte.
  - **Consequência para o DividaAtiva**: a Fase 8 de lá encolhe — deixa de reimplementar o design system à mão e passa a "rodar o `copier update` desta versão e adaptar o que é do domínio da dívida".
  - **Escopo ampliado em 2026-08-23 (operador)**: entra também o **encaixe da navegação** (T-01 da auditoria) — `{% include "core/_nav_dominio.html" %}` como ponto de extensão mais uma inclusion tag `{% item_nav %}` para o item. Motivo: o `_nav.html` é o pior conflito aberto da família (79 linhas reescritas pelo DividaAtiva dentro de arquivo upstream), e resolvê-lo ANTES da v0.2.0 é o que torna o `copier update` dos derivados viável em vez de doloroso. Resolve junto o T-03 (itens do app exemplo saem do `_nav.html` base).
  - **Pendência de release que esta fase carrega**: o repositório está com 37 commits desde a tag `v0.1.0`. Como o Copier lê a última tag e não o HEAD, a Fase 6 inteira (marca, logos, bind mount) nunca chegou a nenhum sistema derivado. A fase deve fechar com uma tag `v0.2.0` que entregue Fase 6 e Fase 7 juntas.

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Init: Template clonável via Copier (não pacote pip, não monorepo)
- Init: Stack fechada idêntica à da PCA (Django 5.2 LTS, PostgreSQL 17, HTMX/Alpine/Tailwind, ECharts)
- Init: `Usuario` customizado desde a primeira migração (preserva viabilidade de SSO futuro)
- Init: PCA em `/opt/web/pca` não será alterada
- Init: Toda documentação e artefatos de planejamento em pt-BR
- [Phase 01-01]: Reproduzida literalmente a topologia de settings/middleware/axes/CSRF da PCA, generalizada e sem menção a domínio
- [Phase 01-01]: requirements.txt restrito às 9 dependências desta fase — sem django-simple-history (Fase 2) e sem openpyxl/freezegun
- [Phase 01-02]: Kernel do app core (Usuario/UsuarioManager, axes_lockout, HtmxRedirectMiddleware, context processor, healthz, base.html com CSRF/htmx) reproduzido verbatim da PCA, sem PcaAdminConfig/login/logout (esses são CORE-03/Fase 2 e Plan 01-04)
- [Phase 01-03]: compose.yml restrito a web+db (sem backup, INF-03/Fase 4); pgdata sem external:true nesta fase (Assumption A4 — clone limpo sobe sozinho)
- [Phase 01-03]: nome de projeto compose herdado do diretório (sistema_base) isola containers/rede/volume de qualquer stack pca_* no mesmo host
- [Phase 01-04]: login_view/logout_view/shell_view reproduzidos verbatim do padrão da PCA, com validação explícita de open redirect em ?next= via url_has_allowed_host_and_scheme
- [Phase 02-01]: COR_PRIMARIA validada com re.fullmatch(#RRGGBB) no boot — ImproperlyConfigured como barreira contra CSS injection via .env (T-02-01)
- [Phase 02-01]: Tokens de marca derivados por misturar() em JS puro no tailwind.config.js — um unico hex literal de identidade (D-17), sem CSS vars (sem dark mode nesta fase)
- [Phase 02-02]: Kernel da fase entrega zero template tags customizadas — D-12 veta templatetag com ORM e a trilha vem pronta da view (item 'template tags' de CORE-04 atendido deliberadamente sem tags)
- [Phase 02-02]: Botão Sair do shell como <form hx-post> com csrf_token de fallback no-JS (padrão IN-02), não botão solto
- [Phase 02-03]: Gate do admin mantido no padrão do Django (is_active and is_staff) — decisão A1 travada por teste; gate superuser é política de domínio, não do template
- [Phase 02-03]: Auditoria padrão: HistoricalRecords() nos modelos de domínio; user model é exceção via simple_history.register() em core/admin.py (dependência circular em model swappable)
- [Phase 02-04]: hx-on::before-request da limpeza de cache no <form hx-post> (elemento emissor), não no <button> — é onde o htmx dispara before-request
- [Phase 02-04]: SW hand-rolled com cache static-v1 restrito a /static/ + fallback offline; navegações nunca gravadas em cache (HTML autenticado jamais persiste no cliente)
- [Phase ?]: O collectstatic recebe somente valores fictícios não secretos no build; o .env substitui-os em runtime.
- [Phase ?]: O preflight usa o contrato focado de collectstatic; a matriz Copier integral roda separadamente por exceder 45 segundos.
- [Phase 06-01]: Bind mount ${PGDATA_DIR:-./dados/pg} substitui o named volume pgdata — down -v não destrói mais o banco (D-73/D-76)
- [Phase 06-01]: .gitignore fora do _exclude do copier.yml; .gitignore.jinja renderiza e protege .env e /dados/ no sistema gerado (D-74)
- [Phase 06-01]: copier copy --vcs-ref=HEAD na rede de testes — com a tag v0.1.0 o Copier copiava a última tag em vez do estado atual do template
- [Phase 06-02]: Logos por arquivo fixo em core/static/img/ (logo-entidade.svg, logo-subsistema.svg) via {% static %} — trocar = substituir o arquivo, sem editar código (D-65); alt sempre via sistema_sigla (D-67)
- [Phase 06-02]: Favicon reaproveita icon-192.png no base.html (D-72) — zero arquivo novo, elimina 302 de /favicon.ico; comentário XML dos SVGs sem hífen duplo (XML proíbe -- em comentário)
- [Phase ?]: [Fase 06-03] Seção única 'Customização de marca' no README gerado absorve a antiga seção de ícones PWA — 5 pontos de marca num só lugar (D-77); PNG não é aceito como logo (contrato nome+extensão SVG fixos)
- [Phase ?]: [Fase 06-03] Migração named volume → bind mount documentada como passo manual (cp -a /de/. /para/ com stack parada) — nenhum script (D-40); one-liner usa sistema_slug_pgdata interpolado no fonte Jinja
- [Phase ?]: Guarda anti-v0.1.0 usa grep -E ancorado ('_commit: v0.1.0(,|$)'), não grep -F substring — o describe correto do HEAD ('v0.1.0-48-gHASH') contém 'v0.1.0' como substring e um -F causaria falso positivo em toda execução correta — Rule 1 - bug encontrado durante Task 2/3

### Pending Todos

None yet.

### Blockers/Concerns

- Agentes GSD não instalados (`npx get-shit-done-cc@latest --global`) — pesquisa e roadmap foram gerados inline; instalar antes de `/gsd:plan-phase` para habilitar researcher/checker/verifier

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260818-2og | Auditoria integral de negócio, produto, operação e escalabilidade; sobrescrever REVIEW.md sem alterar código-fonte | 2026-08-18 | docs-only | [260818-2og-auditar-integralmente-o-sistema-base-com](./quick/260818-2og-auditar-integralmente-o-sistema-base-com/) |
| 260818-n9k | Corrigir vazamento de comentários `{# #}` de template Django exibidos como texto (login e topo da página); causa raiz + teste de regressão | 2026-08-18 | ba86084 | [260818-n9k-corrija-o-vazamento-de-coment-rios-de-te](./quick/260818-n9k-corrija-o-vazamento-de-coment-rios-de-te/) |
| 260818-qc7 | Documentar padrão nginx conf.d + certbot --nginx na seção de publicação do README | 2026-08-18 | 8a52155 | [260818-qc7-documentar-padr-o-nginx-conf-d-certbot-n](./quick/260818-qc7-documentar-padr-o-nginx-conf-d-certbot-n/) |
| 260818-qoy | Adicionar seção 'Os três ciclos de trabalho' ao README do template | 2026-08-18 | f910787 | [260818-qoy-adicionar-se-o-os-tr-s-ciclos-de-trabalh](./quick/260818-qoy-adicionar-se-o-os-tr-s-ciclos-de-trabalh/) |
| 260818-qwd | Documentar criação da tag de release + seção Resumo executável (exemplo financeiro:12010) no README | 2026-08-18 | 44ae507 | [260818-qwd-documentar-cria-o-da-tag-de-release-e-re](./quick/260818-qwd-documentar-cria-o-da-tag-de-release-e-re/) |

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| *(none)* | | | |

## Session Continuity

Last session: 2026-08-23T17:53:20.699Z
Stopped at: Completed 07-01-PLAN.md
Resume file: None
