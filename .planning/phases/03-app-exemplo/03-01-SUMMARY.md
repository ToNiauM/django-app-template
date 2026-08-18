# Phase 3 Plan 01: Fundação de Dados, Infraestrutura e Modelo ItemExemplo Summary

**Completed:** 2026-08-18
**Plan:** 03-01-PLAN.md
**Duration:** ~5 min

## What Was Done

1. **Vendor Assets e Filtros pt-BR (Task 1):**
   - Instalado localmente `core/static/vendor/echarts.min.js` (Apache ECharts 5.x) extraído de `/opt/web/pca`, eliminando qualquer dependência de CDN externa em runtime.
   - Criado `core/templatetags/formatos.py` com os filtros `@register.filter` `moeda` (ex.: `1.234,56`) e `moeda_curta` (ex.: `1,5 mi`, `12,4 mil`), tratando valores nulos e negativos com precisão decimal.
   - Atualizado `tailwind.config.js` para incluir `./apps/**/*.html` no scanner JIT e atualizado `Dockerfile` no estágio `assets` para copiar os templates de `apps/`.

2. **Modelo de Dados e Auditoria (Task 2):**
   - Criado o app `apps.exemplo` com `apps/exemplo/apps.py` (`ExemploConfig`) e registrado em `config/settings/base.py` (`INSTALLED_APPS`).
   - Implementado o modelo `ItemExemplo` em `apps/exemplo/models.py` contendo `titulo`, `descricao`, `categoria` (`CategoriaChoices`), `status` (`StatusChoices`), `valor` com `MinValueValidator(Decimal("0.00"))`, `prazo`, `ativo`, timestamps e `criado_por` (`Usuario`).
   - Auditado automaticamente com `history = HistoricalRecords()` via `django-simple-history`.
   - Registrado no Django Admin customizado via `SimpleHistoryAdmin` em `apps/exemplo/admin.py`.

3. **Migrações, Seed Command e Testes (Task 3):**
   - Gerada a migração `apps/exemplo/migrations/0001_initial.py` criando as tabelas `exemplo_itemexemplo` e `exemplo_historicalitemexemplo`.
   - Implementado o comando de gerenciamento `python manage.py seed_exemplo` com suporte às flags `--limpar` e `--quantidade` (default 25), populando dados representativos e realistas.
   - Criada a suíte `apps/exemplo/tests/test_models.py` cobrindo criação, auditoria histórica (`+` e `~`), validações numéricas, labels de choices e execução do seed (5/5 testes passando).

## Key Files Created / Modified

- `core/static/vendor/echarts.min.js` — bundle local do Apache ECharts 5.x
- `core/templatetags/formatos.py` — filtros `moeda` e `moeda_curta`
- `tailwind.config.js` — content glob adicionado para `./apps/**/*.html`
- `Dockerfile` — cópia de `apps` no build stage de assets
- `config/settings/base.py` — `apps.exemplo.apps.ExemploConfig` em `INSTALLED_APPS`
- `apps/exemplo/models.py` — modelo `ItemExemplo` com escolhas e `HistoricalRecords`
- `apps/exemplo/admin.py` — registro no admin com `SimpleHistoryAdmin`
- `apps/exemplo/migrations/0001_initial.py` — migração inicial do banco
- `apps/exemplo/management/commands/seed_exemplo.py` — comando de seed
- `apps/exemplo/tests/test_models.py` — testes unitários e de auditoria

## Verification

- `docker compose run --rm -v "$PWD:/app" --entrypoint python web manage.py test apps.exemplo.tests.test_models` → 5/5 testes passaram (OK)
- `docker compose up -d --build` → Build do Tailwind gerou CSS completo (9099 bytes) e container subiu com sucesso

## Deviations from Plan

None — implementação seguiu estritamente as decisões D-24, D-32, D-34, D-36.
