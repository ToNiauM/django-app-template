---
phase: 08-exemplo-provado
plan: 01
subsystem: testing
tags: [django, fixture, copier, simple-history, htmx, orm]

# Dependency graph
requires:
  - phase: 03 (app exemplo)
    provides: padrões de CRUD/whitelist/modal 422/dashboard ORM espelhados pelo fixture
  - phase: 07 (design system)
    provides: core.tema.familia_marca — paleta de gráfico servida sem hex
provides:
  - Backend completo do fixture `apps/diarias` em `.template-tests/fixtures/guia/` (12 arquivos Python)
  - Modelo Viagem único com StatusChoices, HistoricalRecords() e clean() de datas (D-01..D-04)
  - Migração 0001_initial escrita à mão (HistoricalViagem + Viagem) incluída no fixture
  - Seed idempotente `seed_diarias` (get_or_create, 14 viagens pt-BR do universo CFC)
  - 5 views @login_required com whitelist de ordenação, modal 422 + HX-Trigger "viagemSalva" e dashboard 100% ORM
affects: [08-02 (templates e testes do fixture), 08-03, 08-04 (prova na cópia), fase 9 (texto do guia)]

# Tech tracking
tech-stack:
  added: []
  patterns: [fixture didático fora do fluxo Copier (zero .jinja), migração shipada à mão provada por makemigrations --check, seed idempotente por chave natural]

key-files:
  created:
    - .template-tests/fixtures/guia/apps/diarias/models.py
    - .template-tests/fixtures/guia/apps/diarias/apps.py
    - .template-tests/fixtures/guia/apps/diarias/admin.py
    - .template-tests/fixtures/guia/apps/diarias/migrations/0001_initial.py
    - .template-tests/fixtures/guia/apps/diarias/management/commands/seed_diarias.py
    - .template-tests/fixtures/guia/apps/diarias/forms.py
    - .template-tests/fixtures/guia/apps/diarias/views.py
    - .template-tests/fixtures/guia/apps/diarias/urls.py
  modified: []

key-decisions:
  - "Sem campo criado_por no modelo Viagem (o exemplo tem FK para AUTH_USER_MODEL): D-01/D-03 vetam entidade relacionada — autoria de alteração vem do history_user do simple-history"
  - "Seed idempotente por chave natural (servidor, destino, data_inicio) com datas derivadas de timezone.localdate() — lista fixa de 14 viagens, zero random"
  - "Dashboard troca o agrupamento por categoria do exemplo por série mensal via TruncMonth(data_inicio) — a segunda dimensão categórica não existe no modelo único (D-01)"
  - "Filtro de status restrito a StatusChoices.values antes de entrar na query (mitigação T-08-P1-01, mais estrito que o getlist cru do exemplo)"

patterns-established:
  - "Fixture didático: código real em .template-tests/fixtures/guia/, sem __init__.py nos diretórios de fixtures (proteção do unittest discover) e sem sufixo .jinja"
  - "Migração inicial shipada com o app: quem segue o guia nunca roda makemigrations; consistência provada depois por makemigrations diarias --check (08-04)"

requirements-completed: [PRV-01]

# Metrics
duration: 5min
completed: 2026-08-26
---

# Phase 08 Plan 01: Backend do fixture apps/diarias Summary

**App Django completo de diárias e passagens (modelo único Viagem com auditoria, admin, forms, 5 views protegidas, urls, migração shipada e seed idempotente) criado como fixture didático em `.template-tests/fixtures/guia/`, espelho arquivo a arquivo do app exemplo.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-08-26T12:00:56Z
- **Completed:** 2026-08-26T12:06:30Z
- **Tasks:** 2
- **Files modified:** 12 (todos criados)

## Accomplishments

- Backend do fixture `apps/diarias` completo: os 12 arquivos Python que o guia da Fase 9 vai ensinar existem antes do texto (PRV-01)
- D-01..D-04 implementados literalmente: modelo único sem FK, status por TextChoices sem transições, servidor como CharField, HistoricalRecords()
- Todas as invariantes de segurança do exemplo preservadas: 5/5 views `@login_required`, ordenação só via `COLUNAS_ORDENACAO_PERMITIDAS.get(...)`, filtro de status restrito a `StatusChoices.values`, form inválido → 422 sem persistência parcial
- Migração `0001_initial.py` escrita à mão com `HistoricalViagem` + `Viagem` (estrutura idêntica à gerada pelo Django para o exemplo, sem criado_por) — Pitfall 6 coberto
- Dashboard 100% ORM: `aggregate` de KPIs, donut por status com `Sum(F(valor_diarias) + F(valor_passagens))`, série mensal por `TruncMonth`, paleta via `core.tema.familia_marca` (zero hex em Python)

## Task Commits

Each task was committed atomically:

1. **Task 1: Modelo Viagem, apps.py, admin, migração inicial e seed** - `8e58d55` (feat)
2. **Task 2: Forms, views (listagem/modal 422/dashboard ORM) e urls** - `8212a98` (feat)

## Files Created/Modified

- `.template-tests/fixtures/guia/apps/diarias/models.py` - StatusChoices + Viagem com HistoricalRecords() e clean() de datas (erro pt-BR em data_fim)
- `.template-tests/fixtures/guia/apps/diarias/apps.py` - DiariasConfig (name "apps.diarias", verbose "Diárias e Passagens")
- `.template-tests/fixtures/guia/apps/diarias/admin.py` - ViagemAdmin(SimpleHistoryAdmin) com list_display/list_filter/search_fields
- `.template-tests/fixtures/guia/apps/diarias/migrations/0001_initial.py` - CreateModel de HistoricalViagem e Viagem, campos idênticos a models.py
- `.template-tests/fixtures/guia/apps/diarias/management/commands/seed_diarias.py` - 14 viagens pt-BR fixas, get_or_create por (servidor, destino, data_inicio)
- `.template-tests/fixtures/guia/apps/diarias/forms.py` - ViagemForm com widgets Tailwind idênticos aos do ItemExemploForm
- `.template-tests/fixtures/guia/apps/diarias/views.py` - listagem paginada (Paginator 10, whitelist, busca Q), modais criar/editar/excluir com HX-Trigger "viagemSalva", dashboard ORM
- `.template-tests/fixtures/guia/apps/diarias/urls.py` - app_name "diarias", 5 rotas do contrato
- `__init__.py` vazios do app, migrations/, management/ e management/commands/ (e NENHUM em fixtures/, guia/ ou guia/apps/)

## Decisions Made

- Sem `criado_por` no modelo (desvio deliberado do exemplo, registrado no plano): D-01/D-03 vetam FK; autoria vem de `history_user`
- Dashboard usa série mensal (`TruncMonth("data_inicio")`) no lugar do agrupamento por categoria do exemplo — o modelo único não tem segunda dimensão categórica
- Filtro de status valida contra `StatusChoices.values` antes da query (endurecimento de T-08-P1-01 em relação ao exemplo)
- Seed sem argumentos `--limpar`/`--quantidade` do exemplo: idempotência por construção substitui a limpeza manual (banco de ensaio é reusado — Pattern 4)

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None — os nomes de template `diarias/*.html` referenciados pelas views são o contrato explícito com o plano 08-02, que os cria.

## Threat Flags

Nenhuma superfície nova fora do `<threat_model>` do plano: T-08-P1-01/02/03 mitigadas (whitelist + values, 5x @login_required, ModelForm + clean() + 422); nenhum pacote instalado (T-08-P1-SC aceito).

## Next Phase Readiness

- Plano 08-02 pode criar templates e testes do app sobre identificadores estáveis: `apps.diarias`, `app_name = "diarias"`, `viagemSalva`, 422, `COLUNAS_ORDENACAO_PERMITIDAS`, contexto do dashboard (`dados_status`, `dados_mensais`, `paleta_graficos`)
- Plano 08-04 prova a consistência migração ↔ modelo com `makemigrations diarias --check --dry-run` na cópia gerada

## Self-Check: PASSED
