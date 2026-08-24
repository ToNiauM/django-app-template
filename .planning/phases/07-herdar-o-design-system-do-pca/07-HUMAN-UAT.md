---
status: partial
phase: 07-herdar-o-design-system-do-pca
source: [07-VERIFICATION.md]
started: 2026-08-23T23:49:20Z
updated: 2026-08-23T23:49:20Z
---

## Current Test

2. O item "Início" do núcleo na migração do DividaAtiva — aguardando decisão do operador

## Tests

### 1. Coerência do `mode: mvp` com o formato do goal da Fase 7
expected: Ou o goal da Fase 7 é reescrito no formato User Story (`As a …, I want to …, so that ….`), ou a linha `**Mode:** mvp` sai da seção da Phase 7 no ROADMAP.md.
result: passed — o operador delegou a escolha; a linha `**Mode:** mvp` foi removida da Phase 7 (2026-08-23). Razão: a fase já foi executada e verificada contra os 8 success criteria, que são o contrato real; reescrever o enunciado de uma fase concluída seria pior que corrigir o metadado. Nota: as Phases 1–6 mantêm `**Mode:** mvp` com a mesma inconsistência — fora do escopo desta correção.

### 2. O item "Início" do núcleo na migração do DividaAtiva para a v0.2.0
expected: Ou o DividaAtiva aceita exibir o item "Início" (rota `core:shell`), ou fica registrado que ele precisará editar `_nav.html` — reabrindo, só para esse item, o conflito de upstream que a fase eliminou para todo o resto.
result: [pending]

## Summary

total: 2
passed: 1
issues: 0
pending: 1
skipped: 0
blocked: 0

## Gaps

*(nenhum — os 8 must-haves foram verificados; os dois itens acima são decisões, não defeitos)*

---

**Nota:** a inspeção visual das 4 telas × 2 temas (07-08 Task 2, `ui_safety_gate`)
já foi executada numa cópia real e aprovada pelo operador em 2026-08-23. Não é
reaberta por este UAT.
