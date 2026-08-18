---
phase: 05-verifica-o-e-documenta-o
plan: 03
subsystem: testing
tags: [checkpoint, human-verify, copier, docker-compose, cleanup, ui-spec]
requires:
  - phase: 05-verifica-o-e-documenta-o
    provides: "tracer .template-tests/test_05_nascimento.sh com modo --keep (05-01) e runbook README canônico (05-02)"
provides:
  - "Evidência humana 32/32 dos estados visuais/interativos do UI-SPEC na cópia Copier real"
  - "Ambiente efêmero do ensaio (containers, rede, volume, destino e credencial) removido de forma confinada e verificada"
affects: [qa-01, qa-02]
actuals:
  tokens: 2600
  tasks: 3
  commits: 1
tech-stack:
  added: []
  patterns: ["checkpoint bloqueante de inspeção humana sobre cópia retida", "finalizador com trap que preserva o primeiro status não zero", "descarte de segredo provado por presença/ausência de variável"]
key-files:
  created:
    - .planning/phases/05-verifica-o-e-documenta-o/05-03-SUMMARY.md
  modified: []
key-decisions:
  - "A aprovação visual foi obtida por inspeção humana no navegador via túnel SSH loopback, sem qualquer automação de navegador nem edição da UI observada."
  - "O diretório-pai mktemp vazio deixado pelo tracer em modo --keep foi removido após o rm do destino exato, mantendo o filesystem sem resíduo do ensaio."
patterns-established:
  - "Checkpoints com credencial efêmera entregam a senha somente no handoff em memória/retorno do checkpoint; nunca em arquivo, log ou SUMMARY."
requirements-completed: [QA-01, QA-02]
coverage:
  - id: D1
    description: "Cópia retida via --keep com superusuário confirmado, 25 itens de ensaio e smokes /healthz e /login/ em loopback."
    requirement: QA-02
    verification:
      - kind: integration
        ref: ".template-tests/test_05_nascimento.sh --keep (exit 0; 72 testes Django)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Os 32 estados do UI-SPEC (17 covered + 15 backstop) confirmados por inspeção humana em login, shell, CRUD, modal e dashboard."
    requirement: QA-02
    verification:
      - kind: manual
        ref: ".planning/phases/05-verifica-o-e-documenta-o/05-UI-SPEC.md — checkpoint human-verify aprovado"
        status: pass
    human_judgment: true
  - id: D3
    description: "Cleanup confinado: down --volumes --remove-orphans no projeto exato, destino removido, zero recursos com o label Compose do ensaio."
    requirement: QA-02
    verification:
      - kind: integration
        ref: "finalizador com trap + verificação por labels + harness sentinela 23"
        status: pass
    human_judgment: false
duration: 15min ativos (com espera do checkpoint humano entre as Tasks 2 e 3)
completed: 2026-08-18
status: complete
---

# Phase 05 Plan 03: Inspeção Humana e Cleanup do Nascimento Summary

**Inspeção humana aprovou 32/32 estados do UI-SPEC na cópia Copier real retida em loopback, e o ambiente efêmero inteiro — containers, rede, volume, destino mktemp e credencial — foi removido com verificação por labels e descarte provado das variáveis.**

## Performance

- **Duration:** 15min de execução ativa (Task 1: ~5min; Task 3: ~1min; intervalo do checkpoint humano entre elas)
- **Started:** 2026-08-18T20:26:10Z
- **Completed:** 2026-08-18T20:41:04Z
- **Tasks:** 3 (2 auto + 1 checkpoint human-verify bloqueante)
- **Files modified:** 0 versionados durante as tasks (somente este SUMMARY ao final)

## Accomplishments

- **Task 1 — cópia retida e populada:** executado `.template-tests/test_05_nascimento.sh --keep` uma única vez com `NASCIMENTO_ADMIN_PASSWORD` gerada por `secrets.token_urlsafe(24)` na sessão e sem tracing; exit 0 após tracer completo (72 testes Django). Extraídos por prefixo, sem `eval` e com exatamente uma ocorrência cada: `NASCIMENTO_DESTINO` (diretório existente sob mktemp), `NASCIMENTO_PROJETO_COMPOSE` (alfanumérico) e `NASCIMENTO_URL` (loopback `http://127.0.0.1:`). Superusuário `nascimento@example.invalid` confirmado com `is_staff`/`is_superuser` via `get_user_model()` sem ler a senha; `seed_exemplo --limpar --quantidade 25` aplicado no serviço `web` do projeto exato (contagem verificada == 25); `/healthz` e `/login/` responderam 200.
- **Task 2 — checkpoint human-verify (gate blocking):** o usuário inspecionou o sistema no navegador via túnel SSH loopback usando a URL, o e-mail contratado e a senha efêmera entregue exclusivamente pelo handoff em memória, e **aprovou explicitamente** ("approved"): os 17 critérios covered e os 15 objetos backstop do UI-SPEC foram reconciliados — 32/32, nenhum identificador `[surface/state]` de falha devolvido. Nenhum template, CSS, JavaScript ou código gerado foi editado para produzir a aprovação.
- **Task 3 — desmontagem confinada:** finalizador `finalizar_cleanup` instalado em `0 HUP INT TERM` com remoção dos próprios traps, `registrar_falha` preservando o primeiro status não zero e `errexit` desabilitado no finally; alvos validados (diretório existente no padrão mktemp do ensaio, fora de raiz/home/workspace; projeto alfanumérico) antes de copiar para variáveis internas com `alvos_validados=1`. `docker compose --project-name nascimento3481424 --env-file .env down --volumes --remove-orphans` retornou 0 no destino exato; `rm -rf --` do caminho validado; pós-verificação por labels `com.docker.compose.project`: 0 containers, 0 redes, 0 volumes; destino inexistente.

## Task Commits

1. **Task 1: Preparar uma cópia retida e populada para inspeção** — sem commit (nenhum arquivo versionado modificado, por design do plano).
2. **Task 2: Verificar visualmente login, shell, CRUD e dashboard** — sem commit (inspeção no navegador; aprovação humana registrada nesta sessão).
3. **Task 3: Desmontar e apagar somente o ambiente inspecionado** — sem commit (remoção de recursos efêmeros apenas).

O único commit do plano é o deste SUMMARY (metadados).

## Files Created/Modified

- `.planning/phases/05-verifica-o-e-documenta-o/05-03-SUMMARY.md` — este registro. Nenhum outro arquivo do checkout foi criado ou modificado pelas três tasks.

## Decisions Made

- A inspeção humana usou exclusivamente a identidade contratada `nascimento@example.invalid` e a senha aleatória do handoff em memória; nenhuma credencial fixa alternativa foi tentada.
- O acesso do usuário ao loopback do servidor deu-se por túnel SSH, preservando o bind exclusivo em `127.0.0.1` (T-05-12).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking/limpeza] Diretório-pai mktemp vazio remanescente do modo `--keep`**
- **Found during:** Task 3 (pós-verificação)
- **Issue:** O tracer cria `TMP=$(mktemp -d)` e retém `TMP/nascimento`; a Task 3 remove o caminho exato `NASCIMENTO_DESTINO`, deixando o pai `mktemp` vazio no filesystem.
- **Fix:** Após confirmar que o pai estava vazio (`ls -A` == 0 entradas), removido com `rmdir` — operação que falha por segurança se houver qualquer conteúdo.
- **Files modified:** nenhum arquivo versionado.
- **Verification:** O caminho do pai deixou de existir; nenhum outro diretório foi tocado.
- **Committed in:** não aplicável (mudança apenas de ambiente).

---

**Total deviations:** 1 auto-fixed (Rule 3, resíduo de ambiente).
**Impact on plan:** Nenhum impacto no escopo; o cleanup ficou mais completo que o mínimo contratado.

## Verification

- Task 1 `<verify>` integral — PASS (`VERIFY_TASK1=PASS`): senha presente em memória, destino existente, projeto não vazio, `/healthz` e `/login/` 2xx, superusuário `is_staff`/`is_superuser` e `ItemExemplo.objects.count() == 25` no serviço `web` do projeto exato.
- Task 2 `<verify>` automatizado — PASS (`VERIFY_TASK2_PRECOND=PASS`); `<human-check>` — **aprovado pelo usuário: 32/32**, sem desvios `[surface/state]`.
- Task 3 `<verify>` — PASS: harness de falha forçada retornou o status sentinela `23` após os quatro `unset` (não mascarado pelo cleanup).
- Pós-cleanup: `docker ps -a` / `network ls` / `volume ls` filtrados por `label=com.docker.compose.project=nascimento3481424` retornaram 0 itens; `NASCIMENTO_DESTINO` inexistente; descarte de `NASCIMENTO_ADMIN_PASSWORD`, `NASCIMENTO_DESTINO`, `NASCIMENTO_PROJETO_COMPOSE` e `NASCIMENTO_URL` confirmado somente por `test -z "${VAR+x}"`, sem ler nem imprimir valores.
- Segurança da credencial (T-05-11): busca recursiva pelo valor da senha no destino, no checkout e no scratchpad retornou zero ocorrências antes do cleanup; a senha jamais foi gravada em arquivo, árvore gerada, README, SUMMARY ou log.
- Proibição QA-02 honrada: nenhum template, estilo ou comportamento foi alterado para produzir aprovação; `git status` ao final mostra apenas artefatos pré-existentes alheios ao plano (`.planning/config.json` de tracking do orquestrador e `IDEIA.md` untracked, ambos intocados por esta execução).

## Known Stubs

None — o plano não cria código; nenhum stub existe.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- QA-01 e QA-02 agora contam com prova automatizada (05-01) e evidência humana complementar 32/32 (este plano); DOC-01 concluído em 05-02.
- A Fase 5 está integralmente executada; nenhum recurso efêmero do ensaio permanece no host.

## Self-Check: PASSED

- Encontrado: `.planning/phases/05-verifica-o-e-documenta-o/05-03-SUMMARY.md`.
- Confirmado: 0 recursos Docker com o label do projeto do ensaio; destino e diretório-pai mktemp inexistentes.

---
*Phase: 05-verifica-o-e-documenta-o*
*Completed: 2026-08-18*
