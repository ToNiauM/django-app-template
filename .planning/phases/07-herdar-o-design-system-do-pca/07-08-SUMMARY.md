---
phase: 07-herdar-o-design-system-do-pca
plan: 08
status: in-progress
subsystem: release-e-documentacao
tags: [readme, roadmap, requirements, release, v0.2.0, checkpoint]
dependency-graph:
  requires: ["07-01", "07-02", "07-03", "07-04", "07-05", "07-06", "07-07"]
  provides: ["roteiro-atualizacao-derivados-v0.1.0", "inventario-suites-medido"]
  affects: ["README.md", ".planning/ROADMAP.md", ".planning/REQUIREMENTS.md"]
tech-stack:
  added: []
  patterns:
    - "Inventário de suítes sempre medido na hora (ls .template-tests/ | grep -c '^test_'), nunca decorado em documento"
key-files:
  created: []
  modified:
    - "README.md"
    - ".planning/ROADMAP.md"
    - ".planning/REQUIREMENTS.md"
decisions:
  - "Contagem de suítes medida no momento da task: 13 (10 herdadas + test_07_tokens.py + test_07_nav_extensao.py + test_07_cor_runtime.sh); nenhum inteiro citado em ROADMAP/REQUIREMENTS — ambos passam a dizer 'todas as suítes de .template-tests/'"
  - "REQUIREMENTS.md linha 70 (QA-03) já estava marcada '- [x]' antes desta task, não '- [ ]' como o plano assumia; preservado o estado do checkbox e trocado apenas o miolo da frase ('as 11 suítes' → 'todas as suítes'), sem reindentar nem mexer no rótulo"
metrics:
  duration: "Task 1 apenas — plano ainda não concluído (checkpoint Task 2 pendente)"
  completed: null
---

# Phase 07 Plan 08: Fecho da fase — roteiro de atualização, inventário medido e tag v0.2.0 Summary

**Status: EM ANDAMENTO.** Este SUMMARY cobre apenas a Task 1 (auto). A Task 2
(`checkpoint:human-verify`, gate="blocking") está com a preparação feita e
aguarda inspeção visual humana real. A Task 3 (regressão completa + tag
`v0.2.0`) ainda não rodou. Este arquivo será completado por um agente de
continuação após a aprovação do operador na Task 2 e a execução da Task 3.

## One-liner

README ganha o roteiro de 8 passos para derivados presos na v0.1.0, a seção
"Regressão do template" passa a listar as 13 suítes reais (medidas, não
decoradas), e ROADMAP/REQUIREMENTS deixam de citar o número falso "11".

## Task 1 — Roteiro de atualização dos derivados, regressão documentada e inventário de suítes medido

Executada e commitada.

- **README.md** — nova subseção "Atualizando um sistema que nasceu na
  v0.1.0" em "Releases e atualização do núcleo", com a tabela dos três
  conflitos previsíveis (`_nav.html`, `tailwind.config.js`, `input.css`) e o
  roteiro de 8 passos citado em `<interfaces>` do plano. Seção "Regressão do
  template" atualizada: linha `ensaio_django.sh derrubar` no início e depois
  da suíte de cor, as três suítes novas da Fase 7 documentadas
  individualmente, nova subseção explicando a ferramenta
  `ensaio_django.sh` (subcomandos, banco que sobrevive entre invocações,
  `derrubar` como limpeza de host), e nota sobre `--vcs-ref=HEAD`. Seção
  "Criando a tag de release" com os exemplos trocados de `v0.1.0` para
  `v0.2.0` e frase explicando o que a release entrega (Fases 6 e 7 juntas).
- **`.planning/ROADMAP.md`** (critério 8) e **`.planning/REQUIREMENTS.md`**
  (QA-03) — "as 11 suítes de `.template-tests/`" trocado por "todas as
  suítes de `.template-tests/`" nos dois documentos. O número "11" já era
  falso antes desta fase (o HEAD tinha 10 suítes no momento da auditoria); a
  troca é limpeza de dívida, não enfraquecimento de critério — "todas as
  suítes" continua valendo para as 13 que existem hoje e para as que
  vierem depois.

**Inventário medido nesta task:** `ls .template-tests/ | grep -c '^test_'`
devolveu **13**: `test_04_03_identity.py`, `test_04_04_optional_exemplo.py`,
`test_04_05_backup.py`, `test_04_06_operations.py`,
`test_04_07_collectstatic.py`, `test_05_nascimento.sh`,
`test_06_persistencia.py`, `test_07_cor_runtime.sh`,
`test_07_nav_extensao.py`, `test_07_tokens.py`, `test_copier_copy.sh`,
`test_copier_update.sh`, `test_quick_comentarios_template.py`.
`ensaio_django.sh` foi excluído de propósito (não é suíte, nome não começa
com `test_`).

### Verificação

- `grep -c 'v0.2.0' README.md` → 6 (≥3 ✓)
- `grep -c '_nav_dominio.html' README.md` → 4 (≥2 ✓)
- `grep -c '_skip_if_exists' README.md` → 1 (≥1 ✓)
- `grep -c 'test_07_tokens.py' README.md` → 1, `test_07_nav_extensao.py` → 1,
  `test_07_cor_runtime.sh` → 3 (todos ≥1 ✓)
- `grep -c 'ensaio_django.sh' README.md` → 4 (≥2 ✓)
- `grep -rc '11 suítes' README.md .planning/ROADMAP.md .planning/REQUIREMENTS.md`
  → 0 em todos ✓
- `grep -c 'todas as suítes' .planning/ROADMAP.md` → 1, mesmo em
  `.planning/REQUIREMENTS.md` → 1 ✓
- `grep -cE '\b(11|14) suítes\b' README.md` → 0 ✓
- `grep -c -- '--vcs-ref=HEAD' README.md` → 2 (≥1 ✓)
- `grep -c 'checkout --theirs' README.md` → 4 (≥1 ✓)
- `bash .template-tests/test_copier_update.sh` → exit 0, e
  `grep -Fq 'A → B → C' README.md` continua verdadeiro (a seção não foi
  quebrada)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - discrepância de estado] Checkbox de QA-03 já vinha `[x]`, não `[ ]`**
- **Found during:** Edição de `.planning/REQUIREMENTS.md`
- **Issue:** O plano assumia (e sua acceptance criteria testava literalmente)
  que a linha começava com `- [ ] **QA-03**:` e que o grep
  `^- \[ \] \*\*QA-03\*\*:.*todas as suítes` deveria retornar 1 após a
  edição. Na prática a linha já estava `- [x] **QA-03**:` antes desta task
  (requisito provavelmente marcado como completo por uma execução anterior
  da fase).
- **Fix:** Preservado o estado real do checkbox (`[x]`) e trocado somente o
  miolo da frase, exatamente como instruído em "não reindente, não troque
  `- [ ]` por `- [x]` e não mexa no rótulo" — a instrução pede para não
  *alterar* o estado do checkbox, então mantive o que já estava lá em vez
  de forçá-lo a `[ ]`.
- **Files modified:** `.planning/REQUIREMENTS.md`
- **Commit:** (ver hash abaixo)

Nenhum outro desvio. As demais mudanças seguiram o plano literalmente.

## Próximos passos (para o agente de continuação)

1. Task 2 (`checkpoint:human-verify`, gate="blocking") — preparação
   (derrubar banco de ensaio anterior, gerar senha efêmera, subir cópia
   retida com `test_05_nascimento.sh --keep`, checagem de vazamento de
   credencial) já foi feita pelo executor. A senha foi entregue ao operador
   **apenas** no retorno estruturado do checkpoint, nunca gravada em
   arquivo. Falta a inspeção visual humana real das 4 telas nos 2 temas.
2. Após aprovação ("aprovado"), rodar a Task 3: regressão completa
   (`ensaio_django.sh derrubar`, `test_copier_copy.sh`,
   `test_copier_update.sh`, suíte Python completa, `test_07_cor_runtime.sh`,
   `ensaio_django.sh derrubar` de novo, `test_05_nascimento.sh` sem
   `--keep`) e, com tudo verde e árvore limpa, criar a tag anotada
   `git tag -a v0.2.0`.
3. Completar este SUMMARY.md com os resultados da Task 2 e da Task 3, e só
   então rodar `roadmap.update-plan-progress` / `requirements.mark-complete`
   / `state.advance-plan` para fechar o plano e a fase.

## Self-Check: PASSED

- FOUND: README.md (modificado, contém as strings verificadas acima)
- FOUND: .planning/ROADMAP.md (critério 8 sem "11 suítes")
- FOUND: .planning/REQUIREMENTS.md (QA-03 sem "11 suítes")
- `bash .template-tests/test_copier_update.sh` executado nesta sessão → exit 0
