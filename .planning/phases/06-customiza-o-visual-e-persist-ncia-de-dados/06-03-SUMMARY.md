---
phase: 06-customiza-o-visual-e-persist-ncia-de-dados
plan: 03
subsystem: docs
tags: [readme, copier, runbook, bind-mount, pwa, logos]

# Dependency graph
requires:
  - phase: 06-01
    provides: "Layout de dados por bind mount (${PGDATA_DIR:-./dados/pg}) e .gitignore gerado — objeto das notas de persistência/migração"
  - phase: 06-02
    provides: "Caminhos fixos dos logos (core/static/img/logo-entidade.svg, logo-subsistema.svg) e favicon via icon-192.png — objeto da seção Customização de marca"
provides:
  - "Seção única '## Customização de marca' no README.md.jinja listando os 5 pontos: logo-entidade.svg, logo-subsistema.svg, icon-*.png + gerar_icones_pwa.py, SISTEMA_NOME/SISTEMA_SIGLA, COR_PRIMARIA (D-77)"
  - "Nome e logo do PWA documentados como customizáveis a partir do core — critério 3 do roadmap fechado por documentação (D-71/D-72)"
  - "Nota de persistência ./dados/pg + PGDATA_DIR + uid 999 na Operação diária do README gerado e no nascimento do README raiz (D-74/D-78)"
  - "Nota de migração named volume → bind mount com one-liner manual cp -a /de/. /para/ (D-75, D-40 — nenhum script)"
  - "core/README.md convenção 5: customização por arquivo de nome fixo e admin sem logo (D-70)"
  - "ops/MIGRACAO.md.jinja atualizado para o layout bind mount, regressão test_04_06 verde"
affects: [operacao, releases-do-template]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Documentação de customização centralizada numa seção canônica do README gerado; os demais docs referenciam-na em vez de duplicar a lista"

key-files:
  created: []
  modified:
    - README.md.jinja
    - README.md
    - core/README.md
    - ops/MIGRACAO.md.jinja

key-decisions:
  - "Seção 'Ícones PWA (opcional)' absorvida pela nova 'Customização de marca' — nenhuma informação perdida, um único lugar canônico (D-77)"
  - "One-liner de migração usa {{ sistema_slug }}_pgdata no README.md.jinja — o render entrega o nome real do volume do sistema (ex.: aurora_pgdata), não um placeholder <slug>"
  - "PNG não é aceito como formato de logo: contrato nome+extensão fixos, com orientação de exportar SVG do vetor original (Open Question 3 do research)"

patterns-established:
  - "Notas de segurança operacional junto do ponto de uso: SVG de fonte confiável na seção de marca; uid 999/permissão 700 na nota de persistência"

requirements-completed: [C1, C2, C3, C4]

# Metrics
duration: 4min
completed: 2026-08-19
---

# Phase 06 Plan 03: Documentação de marca e persistência Summary

**Os quatro documentos do template agora convergem: seção única "Customização de marca" no README gerado (5 pontos, incluindo nome/logo do PWA — critério 3 fechado só com documentação), etapa opcional de logos no nascimento, convenção 5 do core e runbook de migração refletindo o bind mount ./dados/pg.**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-08-19T11:52:57Z
- **Completed:** 2026-08-19T11:56:30Z
- **Tasks:** 3/3
- **Files modified:** 4

## Accomplishments

- D-77 entregue: uma única seção `## Customização de marca` no README gerado lista TODOS os pontos (logo da entidade, logo do subsistema, 3 ícones PWA + gerador, nome via SISTEMA_NOME/SISTEMA_SIGLA, cor via COR_PRIMARIA), com as três notas operacionais (rebuild em produção, SVG-only, SVG de fonte confiável)
- Critério 3 do roadmap fechado: logo e nome do PWA documentados como customizáveis a partir do core — mecanismo já existia (D-71/D-72), o plano fechou o componente "documentado"
- Nascimento (README raiz) ganhou o passo 9 opcional "Insira os logos oficiais" antes do commit inicial (renumeração 10–16) e a nota de persistência `./dados/pg` na subida da stack; o resumo executável ganhou a linha de comentário equivalente (D-78)
- `core/README.md` registra a convenção 5 (arquivo de nome fixo é o contrato; admin deliberadamente sem logo — D-70) com texto 100% neutro
- Runbook de migração explica o layout bind mount (PGDATA_DIR, criação automática, sobrevivência a down -v, uid 999/700) sem tocar nos comandos canônicos; seção 6 esclarece que o ensaio de restore não toca `./dados/pg`
- Migração named volume → bind mount documentada como passo manual consciente (`cp -a /de/. /para/` com a stack parada), nenhum script (D-40)

## Task Commits

Each task was committed atomically:

1. **Task 1: README.md.jinja — Customização de marca, persistência e migração** - `f7b3992` (docs)
2. **Task 2: README do template (nascimento) e convenções do core** - `a8d32e9` (docs)
3. **Task 3: Runbook de migração atualizado para o layout bind mount** - `cc3b241` (docs)

## Files Created/Modified

- `README.md.jinja` - Nova seção `## Customização de marca` (absorve `## Ícones PWA (opcional)`); parágrafo de persistência na Operação diária; nota de migração com one-liner em Atualizações do template
- `README.md` - Passo 9 opcional de logos (renumeração 10–16); nota `./dados/pg` no passo 12; comentário opcional no resumo executável; âncora A → B → C intacta
- `core/README.md` - Intro atualizada para "5 convenções"; nova `## 5. Pontos de customização de marca — arquivos de nome fixo`
- `ops/MIGRACAO.md.jinja` - Parágrafo do named volume `pgdata` substituído pela explicação do bind mount; frase de isolamento do ensaio na seção 6

## Decisions Made

- A seção antiga de ícones PWA foi absorvida (não duplicada) pela seção de marca — todo o conteúdo original migrou para o item "Ícones do PWA"
- O one-liner de migração usa `{{ sistema_slug }}_pgdata` no fonte Jinja para o README renderizado mostrar o nome real do volume do sistema
- Intro do `core/README.md` corrigida de "4 convenções" para "5 convenções" ao adicionar a nova convenção (consistência interna do documento)

## Deviations from Plan

None - plan executed exactly as written.

## Verification

- `python3 -m unittest discover -s .template-tests -p 'test_04_06_operations.py'` → OK (2 testes)
- `grep -iE 'pca|cfc|sistema.base'` → vazio em README.md.jinja, core/README.md e ops/MIGRACAO.md.jinja
- Render de fumaça com `copier copy --vcs-ref=HEAD` (sistema "aurora"): todos os tokens obrigatórios do test_04_06 presentes no `ops/MIGRACAO.md` renderizado, seção de marca completa no `README.md` renderizado, `aurora_pgdata` interpolado, zero identidade proibida — validação necessária porque o test_04_06 ainda renderiza da tag v0.1.0 (item já registrado em `deferred-items.md` do 06-01, fora do escopo deste plano)
- Consistência entre os 4 docs conferida por grep: mesmos nomes de arquivo/variável dos planos 06-01/06-02 (logo-entidade.svg, logo-subsistema.svg, icon-*.png, SISTEMA_NOME, SISTEMA_SIGLA, COR_PRIMARIA, PGDATA_DIR, ./dados/pg)

## Known Stubs

Nenhum — plano 100% documentação, sem placeholders pendentes.

## Threat Flags

Nenhuma superfície nova: T-06-07/T-06-08/T-06-09 mitigados conforme o threat model do plano (notas de `./dados/pg`/uid 999, nota de SVG confiável, nota de migração manual).

## Next Phase Readiness

- Fase 06 completa (3/3 planos): critérios 1–4 do roadmap com mecanismo (06-01/06-02) e documentação (06-03) entregues
- Pendência conhecida da fase em `deferred-items.md`: 4 testes Copier ainda pinados na tag v0.1.0 (`--vcs-ref=HEAD` sugerido) — só afeta a rede de regressão, não os sistemas gerados

## Self-Check: PASSED

Arquivos modificados, SUMMARY e commits f7b3992/a8d32e9/cc3b241 verificados no repositório.
