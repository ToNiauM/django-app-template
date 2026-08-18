---
phase: 04-templatiza-o-copier
plan: 07
subsystem: testing
tags: [copier, git, template, regression, docker-compose]
requires:
  - phase: 04-06
    provides: "operações portáteis de restore, TLS e migração renderizadas pelo template"
provides:
  - "matriz repetível de Copier copy para variantes com e sem app exemplo"
  - "ensaio Git/Copier isolado A→B→C com avanço de _commit e opt-out persistente"
affects: [05-qualidade-e-documentacao, release-do-template]
actuals:
  tokens: 4249
  tasks: 2
  commits: 4
tech-stack:
  added: []
  patterns: ["harness POSIX isolado em mktemp com trap", "updates Copier serializados em Git limpo"]
key-files:
  created:
    - .template-tests/test_copier_copy.sh
    - .template-tests/test_copier_update.sh
  modified:
    - README.md
key-decisions:
  - "A auditoria de identidade usa limites lexicais case-insensitive para distinguir identificadores reais de substrings em valores neutros."
  - "Somente _src_path em .copier-answers.yml é neutralizado na auditoria porque é metadado obrigatório do Copier para update."
  - "O ensaio commita .copier-answers.yml explicitamente, inclusive quando arquivos locais são ignorados."
patterns-established:
  - "Toda mudança do template deve passar pelas matrizes copy e update antes de receber tag."
requirements-completed: [TPL-01, TPL-02, TPL-03, TPL-04, INF-03, INF-04]
coverage:
  - id: D1
    description: "Matriz Copier copy de variantes, validators, exclusões, neutralidade e operações renderizadas."
    requirement: TPL-01
    verification:
      - kind: integration
        ref: .template-tests/test_copier_copy.sh
        status: pass
    human_judgment: false
  - id: D2
    description: "Atualização Copier A→B→C isolada, com mudança real de núcleo e app exemplo permanentemente removido."
    requirement: TPL-03
    verification:
      - kind: integration
        ref: .template-tests/test_copier_update.sh
        status: pass
    human_judgment: false
duration: 14min
completed: 2026-08-18
status: complete
---

# Phase 04 Plan 07: Provas Copier Summary

**Matrizes POSIX de copy e update validam projetos gerados, operações portáteis e a sincronização Git A→B→C sem ressuscitar o app exemplo.**

## Performance

- **Duration:** 14min
- **Started:** 2026-08-18T14:20:43-03:00
- **Completed:** 2026-08-18T17:34:51Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Criou uma matriz real de `copier copy` para variantes true/false, validators, exclusões, identidade, Compose, compilação e restore simulado.
- Varre paths e conteúdos case-insensitivamente, reportando todas as ocorrências de identificadores legados como unidades lexicais antes de falhar.
- Executou o ensaio temporário A→B→C: cada estado foi commitado limpo, `_commit` avançou, as mudanças B/C chegaram e o opt-out do exemplo persistiu.
- Documentou no README os comandos de regressão, Git limpo, serialização de updates e recuperação auditável após interrupção.

## Task Commits

1. **Task 1: Automatizar matriz de copier copy e invariantes geradas**
   - `ede4cd7` `test(04-07): add failing Copier copy matrix`
   - `6d8856d` `feat(04-07): verify Copier copy invariants`
2. **Task 2: Provar update A→B→C e não-ressurreição do app**
   - `ceac3db` `test(04-07): add failing Copier update rehearsal`
   - `d4b1041` `feat(04-07): prove Copier update lifecycle`

## Files Created/Modified

- `.template-tests/test_copier_copy.sh` — matriz renderizada e auditoria integral das duas variantes.
- `.template-tests/test_copier_update.sh` — repositórios/tags temporários A/B/C, commits e detector de conflitos inline.
- `README.md` — procedimentos repetíveis de regressão, atualização serializada e recuperação por Git.

## Decisions Made

- Auditoria lexical evita falsos positivos em substrings neutras, mantendo a lista explícita e a busca case-insensitive.
- `_src_path` é a única exceção limitada na leitura de `.copier-answers.yml`, pois registra a origem necessária ao algoritmo de update e não integra a identidade do sistema.
- O harness força o stage de `.copier-answers.yml` no repositório temporário para comprovar o contrato de atualização mesmo sob regras de ignore locais.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] O commit inicial do destino deixava as respostas Copier fora do índice Git.**

- **Found during:** Task 2
- **Issue:** Sem o stage explícito de `.copier-answers.yml`, o update recusava o destino como sujo, embora o estado A tivesse sido commitado.
- **Fix:** O harness adiciona o arquivo de respostas explicitamente antes de cada commit A/B/C.
- **Files modified:** `.template-tests/test_copier_update.sh`
- **Verification:** Ensaio A→B→C passou com estado limpo antes dos updates e depois de cada commit.
- **Committed in:** `d4b1041`

**Total deviations:** 1 auto-fixed (Rule 1).

## Issues Encountered

- O segundo update C consumiu mais tempo que a tentativa curta; a repetição diagnóstica isolada com limite de 180 s concluiu com sucesso e o `trap` removeu a raiz temporária. Nenhuma tag ou checkout real foi alterado.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- O template tem provas executáveis para copy, update, operações e neutralidade antes de releases semver.
- A Fase 5 pode reutilizar o fluxo de nascimento documentado e os dois comandos de regressão.

## Self-Check: PASSED

- Encontrados: `.template-tests/test_copier_copy.sh`, `.template-tests/test_copier_update.sh`, `README.md`.
- Encontrados: `ede4cd7`, `6d8856d`, `ceac3db`, `d4b1041` no histórico Git.

---
*Phase: 04-templatiza-o-copier*
*Completed: 2026-08-18*
