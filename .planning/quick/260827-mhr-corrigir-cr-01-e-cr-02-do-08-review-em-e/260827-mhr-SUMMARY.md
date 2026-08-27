---
phase: quick-260827-mhr
plan: 01
status: complete
subsystem: crud-listagem
tags: [htmx, hx-trigger, querystring, ordenacao, filtros, fixture-guia]
requires:
  - "App de referência apps/exemplo (Fase 03/07) e fixture canônico apps/diarias (Fase 08)"
provides:
  - "CR-01 corrigido: extrair_querystring_filtros exclui também ordem — alternância de ordenação nos cabeçalhos volta a funcionar após o primeiro sort/filtro"
  - "CR-02 corrigido: hx-trigger único e vivo no <form id=form-filtros> (submit + debounce 300ms na busca + change nos selects via from:find) — busca e filtros voltam a disparar GET HTMX no htmx 1.9.12"
affects:
  - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/views.py"
  - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_filtros.html"
  - .template-tests/fixtures/guia/apps/diarias/views.py
  - .template-tests/fixtures/guia/apps/diarias/templates/diarias/_filtros.html
tech-stack:
  added: []
  patterns:
    - "Gatilhos htmx vivem no elemento dono do verbo AJAX (o form com hx-get), nunca soltos em controles sem verbo — hx-trigger naked é no-op no htmx 1.9.12"
    - "ordem é reanexada explicitamente pelos templates (?ordem={novo}&…) e nunca viaja dentro de querystring_filtros — evita parâmetro duplicado onde o Django devolve o último valor"
key-files:
  created: []
  modified:
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/views.py"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_filtros.html"
    - .template-tests/fixtures/guia/apps/diarias/views.py
    - .template-tests/fixtures/guia/apps/diarias/templates/diarias/_filtros.html
key-decisions:
  - "Fix idêntico byte a byte nos views.py e equivalente modulo domínio nos templates — exemplo e diarias permanecem espelhos, como exige o guia"
  - "Seletores from:find adaptados aos names reais: exemplo carrega change para categoria E status; fixture só status"
  - "Nenhum teste precisou mudar: nenhum teste assertava o markup antigo nem a assinatura do helper (grep de planejamento confirmado pela suíte verde sem edição extra)"
metrics:
  duration: 6min
  completed: 2026-08-27
---

# Quick Task 260827-mhr: Corrigir CR-01 e CR-02 do 08-REVIEW em Espelho Summary

CR-01 (ordem duplicada na querystring anulava a alternância de ordenação) e CR-02 (hx-trigger naked sem verbo AJAX era no-op — busca e selects não disparavam requisição) corrigidos em espelho no app de referência e no fixture diarias do guia; suíte integral de 48 testes verde em 276s, incluindo o test_08 de ponta a ponta sobre a cópia de ensaio reconstruída.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | CR-01 — excluir `ordem` da querystring de filtros | 9ff84eb | os 2 views.py (exemplo + fixture) |
| 2 | CR-02 — gatilhos vivos no form dono do hx-get | 42e5653 | os 2 _filtros.html (exemplo + fixture) |
| 3 | Suíte integral .template-tests verde | (sem mudança de código) | — |

## What Was Built

### views.py × 2 (Task 1 — +2/-1 linhas por arquivo, idênticas)

- Assinatura de `extrair_querystring_filtros` passou de `excluir=("pagina",)` para `excluir=("pagina", "ordem")`.
- Comentário pt-BR imediatamente acima do `def`: "ordem é reanexada explicitamente pelos templates e nunca deve viajar dentro da querystring de filtros."
- Docstring e corpo intactos; nada mais tocado (WR-02/WR-03/IN-* fora do escopo por decisão do operador).
- Efeito: os cabeçalhos de tabela montam `?ordem={novo}&{{ querystring_filtros }}` — sem o fix, `ordem` aparecia duplicado e o Django devolvia o ÚLTIMO valor (o antigo), tornando o segundo clique de sort um no-op.

### _filtros.html × 2 (Task 2 — +1/-3 no exemplo, +1/-2 no fixture)

- `<form id="form-filtros">` (dono de `hx-get`/`hx-target`/`hx-swap`/`hx-push-url`, todos preservados) ganhou o único `hx-trigger` do template:
  - exemplo: `submit, input changed delay:300ms from:find input[name='q'], change from:find select[name='categoria'], change from:find select[name='status']`
  - fixture: `submit, input changed delay:300ms from:find input[name='q'], change from:find select[name='status']`
- Removidos os `hx-trigger` órfãos dos controles (input `q` e selects) — sem verbo AJAX no mesmo elemento, eram no-op no htmx 1.9.12.
- Nenhum hex novo, nenhuma classe alterada, nenhum outro atributo tocado; templates equivalentes modulo domínio.

### Verificação (Task 3)

- `python3 -m unittest discover -s .template-tests -p 'test_*.py'` → **Ran 48 tests in 276.324s — OK** (exit 0), rodada em background com o rebuild da cópia de ensaio disparado pelo drift do fixture.
- Greps do plano confirmados: `excluir=("pagina", "ordem")` = 1 por views.py; `hx-trigger` = 1 por template (só no form); `select[name='categoria']` = 1 no exemplo / 0 no fixture; `hx-trigger="change"` = 0 nos dois.
- Contingência de testes não disparou: nenhum teste assertava o comportamento antigo.

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None — nenhuma alteração introduz valor vazio, placeholder ou componente sem fonte de dados.

## Threat Flags

Nenhum — as mudanças só removem `ordem` do echo da querystring (a whitelist `COLUNAS_ORDENACAO_PERMITIDAS` segue como única porta do `order_by`, intocada) e os valores de `hx-trigger` são estáticos, sem interpolação de entrada do usuário (T-qmhr-01 mitigado por construção, T-qmhr-02 aceito conforme o plano).

## Self-Check: PASSED

- 4 arquivos alvo + SUMMARY.md presentes no disco
- Commits 9ff84eb (CR-01) e 42e5653 (CR-02) presentes no histórico
- Suíte integral verde (48 testes, OK, exit 0)
