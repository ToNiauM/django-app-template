---
phase: 08-exemplo-provado
plan: 02
subsystem: testing
tags: [django-templates, htmx, alpine, tailwind, echarts, json-script, unittest]

# Dependency graph
requires:
  - phase: 08-exemplo-provado/01
    provides: backend do fixture apps/diarias (views, urls, forms, modelo Viagem, seed_diarias) cujos identificadores os templates e testes consomem
  - phase: 07 (design system)
    provides: tokens de cor por var CSS, paleta via json_script, decisões 07-06/07-07/07-12 espelhadas byte a byte
  - phase: 03 (app exemplo)
    provides: os 6 templates e as 3 suítes de teste que são o contrato de design desta fase
provides:
  - 6 templates em `.template-tests/fixtures/guia/apps/diarias/templates/diarias/` espelhando 1:1 o app exemplo no domínio de viagens
  - Dashboard ECharts com json_script id="paleta-graficos", esc() em todo formatter e reconstrução em tema:alterado
  - 3 suítes de teste internas (test_models, test_crud, test_dashboard) prontas para `manage.py test apps.diarias` na cópia
affects: [08-03 (instalação na cópia), 08-04 (prova real in-container), fase 9 (guia cita estes arquivos)]

# Tech tracking
tech-stack:
  added: []
  patterns: [espelhamento 1:1 do app exemplo como contrato visual, listener Alpine @viagem-salva.window para HX-Trigger camelCase, série mensal com degraus da rampa da marca sem hex]

key-files:
  created:
    - .template-tests/fixtures/guia/apps/diarias/templates/diarias/viagem_listar.html
    - .template-tests/fixtures/guia/apps/diarias/templates/diarias/_tabela_resultado.html
    - .template-tests/fixtures/guia/apps/diarias/templates/diarias/_filtros.html
    - .template-tests/fixtures/guia/apps/diarias/templates/diarias/_form_modal.html
    - .template-tests/fixtures/guia/apps/diarias/templates/diarias/_confirmar_exclusao_modal.html
    - .template-tests/fixtures/guia/apps/diarias/templates/diarias/dashboard.html
    - .template-tests/fixtures/guia/apps/diarias/tests/__init__.py
    - .template-tests/fixtures/guia/apps/diarias/tests/test_models.py
    - .template-tests/fixtures/guia/apps/diarias/tests/test_crud.py
    - .template-tests/fixtures/guia/apps/diarias/tests/test_dashboard.py
  modified: []

key-decisions:
  - "Botão de perigo do modal de exclusão usa text-red-50 (par nativo de bg-red-600), não o branco puro que o exemplo ainda carrega — o veto da Fase 7 ao branco puro vale para o fixture e o comentário didático evita citar a classe por extenso (padrão 07-11 de não reintroduzir o literal vetado)"
  - "Gráfico de barras mensais tem DUAS séries (diárias e passagens) pintadas com degraus 0 e 2 da rampa_status servida por json_script, com fallback para var(--cor-brand) — zero hex, mesma fonte do donut"
  - "Rótulo do mês derivado do ISO por fatiamento de string (slice), nunca new Date(iso) — Date aplicaria fuso e poderia recuar o rótulo um mês"
  - "Sem drill-down no gráfico mensal: a listagem não filtra por mês; o padrão de drill-down fica só no donut de status, onde a rota de destino sabe responder (comentário didático no template explica o porquê)"
  - "test_crud não asserta a mensagem exata do validador de valor negativo (texto do Django, sujeito a tradução) — asserta 422 + template + mensagem de campo obrigatório + a mensagem própria do clean() de datas, que o fixture controla"

# Metrics
duration: 9min
completed: 2026-08-26
---

# Phase 08 Plan 02: Camada visual e testes do fixture diárias Summary

Seis templates espelhados 1:1 do app exemplo no domínio de viagens (listagem "Diárias e passagens", tabela server-side, filtros, modais 422/HX-Trigger, dashboard ECharts com paleta-graficos) mais três suítes de teste internas cobrindo 302/200, 422, viagemSalva, whitelist, auditoria e seed idempotente.

## O que foi construído

**Task 1 — Templates de CRUD (5 arquivos, commit 9c99c4c):**
- `viagem_listar.html`: H1 exato "Diárias e passagens" (contrato do smoke 08-04), botão "Nova viagem" por `hx-get`, listener `@viagem-salva.window` que redispara os filtros após salvar.
- `_tabela_resultado.html`: colunas servidor+motivo, destino, período (d/m/Y–d/m/Y), diárias e passagens em R$ via filtro `moeda` do core, badges de status (PAGA=emerald, APROVADA=amber, CANCELADA=red, SOLICITADA=neutra); ordenação emite só chaves de `COLUNAS_ORDENACAO_PERMITIDAS`; paginação preserva `querystring_filtros` + `ordem`; estado vazio com "Limpar filtros".
- `_filtros.html`: busca `q` com debounce 300ms sobre servidor/destino/motivo, select de status compatível com `getlist`, hidden `ordem`.
- `_form_modal.html`: fluxo 422 integral do exemplo com `hx-post` para `diarias:viagem_criar`/`viagem_editar`, `{% csrf_token %}`, erros por campo e non_field_errors.
- `_confirmar_exclusao_modal.html`: confirmação com POST + CSRF e HX-Trigger.

**Task 2 — dashboard.html (commit 9e213a4):**
- `json_script` triplo: `dados-mensais`, `dados-status` e o id contratual `paleta-graficos`.
- Chrome 100% via `lerVarCss`/`getComputedStyle`; `corCard` declarada DENTRO de `montarGraficos()`; `dispose()+init()` e nova montagem no evento `tema:alterado`; `esc()` em TODA interpolação de formatter, inclusive numéricas; zero hex no template/JS.
- KPIs: total de viagens, total em diárias, total em passagens, taxa de pagamento. Donut de status com drill-down `?status=`.

**Task 3 — Testes internos (commit 54a50b0):**
- `test_models.py`: criação válida, `full_clean()` reprovando data_fim < data_inicio e valor negativo, history +/~ (D-04), `call_command("seed_diarias")` duas vezes → contagem estável e > 0.
- `test_crud.py`: 302 anônimo nas 5 rotas via subTest, fragmento vs shell por header HTMX, busca, filtro multi-status (inclusive valor desconhecido descartado), whitelist com fallback para entrada maliciosa, paginação preservando filtros, 422 (obrigatório e período invertido), `HX-Trigger == "viagemSalva"` em criar/editar/excluir.
- `test_dashboard.py`: KPIs e agregações por status e mensais (TruncMonth) exatas, banco vazio → 200 com zeros, rampa 4 hex nos dois temas, pertinência da COR_PRIMARIA na rampa clara, `id="paleta-graficos"` com JSON válido, views.py sem hex literal.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Conformidade Fase 7] Botão de perigo sem a classe de branco puro**
- **Found during:** Task 1 (_confirmar_exclusao_modal.html)
- **Issue:** O template ATUAL do exemplo ainda usa a classe vetada de branco puro no botão "Sim, excluir item" (`bg-red-600`); copiar byte a byte reprovaria o gate do plano
- **Fix:** `text-red-50` (par nativo da paleta red do Tailwind), com comentário didático que não cita o literal vetado
- **Files modified:** `_confirmar_exclusao_modal.html`
- **Commit:** 9c99c4c

**2. [Rule 1 - Bug] Comentário didático reintroduzia o literal vetado**
- **Found during:** Task 1 (verificação)
- **Issue:** A primeira versão do comentário citava a classe vetada por extenso, e o grep de aceitação (`grep -RE '...|text-white'`) reprovava o arquivo — mesma classe de falso positivo da decisão 07-11
- **Fix:** Comentário reescrito como "classe de branco puro", sem o literal
- **Files modified:** `_confirmar_exclusao_modal.html`
- **Commit:** 9c99c4c

## Verificação

- 6 templates + 4 arquivos de teste com os nomes exatos do contrato — OK
- `grep -RF 'exemplo:'` e `grep -RF 'itemSalvo'` no fixture: zero ocorrências
- `grep -RE 'bg-ink/40|shadow-xs|backdrop-blur-xs|text-white'` nos templates: zero
- `grep -RE '#[0-9a-fA-F]{6}'` nos templates: zero hex
- `python3 -m py_compile` das 3 suítes: exit 0
- `reverse("diarias:` em test_crud.py: 9 ocorrências (≥ 5)

## Known Stubs

Nenhum — todos os templates estão ligados às views do 08-01 e todos os testes exercitam código real. A prova de execução (rodar as suítes dentro da cópia) é, por design do plano, responsabilidade do 08-04.

## Threat Flags

Nenhuma superfície nova além do threat model do plano: T-08-P2-01 mitigado por `esc()` em todo formatter; T-08-P2-02 por `{% csrf_token %}` nos dois modais (CSRF do HTMX herdado do `htmx:configRequest` de base.html); T-08-P2-03 provado por `test_todas_as_rotas_exigem_autenticacao`.

## Self-Check: PASSED

- FOUND: os 10 arquivos criados (6 templates + 4 de teste)
- FOUND: commits 9c99c4c, 9e213a4, 54a50b0
