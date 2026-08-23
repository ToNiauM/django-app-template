---
phase: 07-herdar-o-design-system-do-pca
plan: 01
subsystem: testing
tags: [copier, docker-compose, django, shell, sha1, template-tests]

# Dependency graph
requires: []
provides:
  - "As quatro suítes de .template-tests/ que renderizam via copier copy agora usam --vcs-ref=HEAD (working tree), não a tag v0.1.0"
  - "Guarda executável em test_copier_copy.sh que falha ruidosamente se a árvore gerada vier de uma tag antiga"
  - ".template-tests/ensaio_django.sh — banco de ensaio reutilizável para rodar qualquer alvo Django dentro de uma cópia real do template"
affects: [07-03, 07-04, 07-05, 07-06, 07-07, 07-08]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Fingerprint de working tree via git ls-files -z -co --exclude-standard | LC_ALL=C sort -z | python3 (caminho+conteúdo, marcador AUSENTE sem separador para caminho apagado sem git rm, sem metadados)"
    - "Ferramenta de teste não-suíte (prefixo sem test_) com contrato de subcomandos em stdout limpo, diagnóstico em stderr"
    - "Reúso condicional de ambiente Docker Compose efêmero: cópia+fingerprint+healthz como critério de validade, sem trap de limpeza automática"

key-files:
  created:
    - .template-tests/ensaio_django.sh
  modified:
    - .template-tests/test_copier_copy.sh
    - .template-tests/test_04_03_identity.py
    - .template-tests/test_04_04_optional_exemplo.py
    - .template-tests/test_04_06_operations.py

key-decisions:
  - "Guarda anti-v0.1.0 usa grep -E ancorado ('_commit: v0\\.1\\.0(,|$)'), não grep -F substring — o describe correto do HEAD ('v0.1.0-48-gHASH') contém 'v0.1.0' como substring e um -F causaria falso positivo em toda execução correta"
  - "testar/executar/compor chamam garantir_banco() (mesma lógica de reúso-ou-recriação de subir/porta/url/destino) — a prova negativa de frescor do próprio plano exige que 'testar' sozinho detecte fingerprint desatualizado e recrie, sem exigir um 'subir' anterior"
  - "compose(), diagnosticar() e o formato do laço aguardar_web() foram copiados de test_05_nascimento.sh; PORTA e PROJETO são persistidos em arquivos de estado (não recalculados deterministicamente) para bater com o contrato de <interfaces>"
  - "O script Python do fingerprint vive num arquivo próprio (STATE_DIR/_fingerprint.py), não num heredoc anexado a 'python3 -' — um heredoc no mesmo comando substituiria o stdin que carrega a lista de caminhos vinda do pipe"

patterns-established:
  - "Prova negativa registrada em SUMMARY como evidência de que a asserção realmente falha quando deveria (não só que passa quando deveria)"

requirements-completed: [QA-03, REL-01]

# Metrics
duration: 18min
completed: 2026-08-23
---

# Phase 07 Plan 01: Corrigir o vcs-ref e criar o banco de ensaio Summary

**As quatro suítes que geravam sistemas a partir da tag v0.1.0 passam a gerar do working tree (--vcs-ref=HEAD), com guarda executável contra regressão, e a fase ganha `ensaio_django.sh` — um comando único que renderiza, sobe e roda qualquer alvo Django dentro de uma cópia real do template.**

## Performance

- **Duration:** 18 min
- **Started:** 2026-08-23T17:33:00Z
- **Completed:** 2026-08-23T17:51:00Z
- **Tasks:** 3
- **Files modified:** 5 (4 modificados, 1 criado)

## Accomplishments
- `test_copier_copy.sh`, `test_04_03_identity.py`, `test_04_04_optional_exemplo.py` e `test_04_06_operations.py` renderizam com `--vcs-ref=HEAD`; `exigir_invalido()` e `test_copier_update.sh` ficaram intocados de propósito (ensaio A→B→C com tags próprias)
- `exigir_variante()` em `test_copier_copy.sh` ganhou duas asserções (logo da Fase 6 presente + `_commit` diferente de `v0.1.0`) que valem para as duas variantes de `incluir_app_exemplo`
- `.template-tests/ensaio_django.sh` criado: 8 subcomandos (`subir`, `porta`, `url`, `destino`, `testar`, `executar`, `compor`, `derrubar`), impressão digital de conteúdo do working tree, reúso condicional e recriação completa quando necessário

## Task Commits

Each task was committed atomically:

1. **Task 1: Apontar as quatro suítes para o working tree** - `b336a7d` (fix)
2. **Task 2: Guarda executável contra a regressão do --vcs-ref** - `c52ed5d` (feat)
3. **Task 3: Banco de ensaio — um comando para rodar suíte Django da cópia gerada** - `9942543` (feat)

**Plan metadata:** commit pendente (docs: complete plan)

## Files Created/Modified
- `.template-tests/test_copier_copy.sh` - `copiar()` usa `--vcs-ref=HEAD`; `exigir_variante()` ganhou a guarda anti-v0.1.0
- `.template-tests/test_04_03_identity.py` - `render()` usa `--vcs-ref=HEAD`
- `.template-tests/test_04_04_optional_exemplo.py` - `render()` usa `--vcs-ref=HEAD`
- `.template-tests/test_04_06_operations.py` - `render()` (método) usa `--vcs-ref=HEAD`
- `.template-tests/ensaio_django.sh` - banco de ensaio: renderiza, sobe Compose, publica porta, roda alvo Django, propaga código de saída

## Decisions Made
- Ver `key-decisions` no frontmatter — destaque para a correção do bug de substring na guarda (Rule 1, ver Deviations)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Guarda anti-v0.1.0 com falso positivo por grep -F substring**
- **Found during:** Task 2 (Guarda executável contra a regressão do --vcs-ref)
- **Issue:** A primeira implementação usou `grep -Fq '_commit: v0.1.0'`. Como `grep -F` faz correspondência de substring, ela também batia em `_commit: v0.1.0-48-g3014d27` — o describe **correto** do HEAD quando `--vcs-ref=HEAD` está funcionando. Resultado: a guarda reprovava toda execução correta, não só a regressão que deveria detectar.
- **Fix:** Trocado para `grep -Eq '_commit: v0\.1\.0(,|$)'`, ancorando no separador YAML (vírgula) ou fim de linha, para exigir a tag exata `v0.1.0` e não um prefixo dela.
- **Files modified:** `.template-tests/test_copier_copy.sh`, `.template-tests/ensaio_django.sh` (mesma asserção replicada na Task 3)
- **Verification:** `bash .template-tests/test_copier_copy.sh` passou (exit 0) após a correção; prova negativa (remover `--vcs-ref=HEAD` temporariamente) confirmou que a guarda ainda falha corretamente pela primeira asserção (logo ausente) quando a flag falta
- **Committed in:** `c52ed5d` (Task 2), `9942543` (Task 3)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Correção essencial — sem ela a guarda reprovaria toda execução legítima da suíte e do banco de ensaio, quebrando o objetivo do próprio plano.

## Issues Encountered
- Nenhum bloqueio; recriações do banco de ensaio (Task 3) ficaram bem abaixo do teto de 600000ms em todas as invocações desta sessão (cache Docker já aquecido por execuções anteriores da suíte `test_copier_copy.sh`/`test_04_*`), então o fallback de background+polling não precisou ser acionado após a primeira criação — mas foi usado preventivamente em toda invocação que pudesse recriar, conforme a regra do plano.

## Provas Negativas Registradas

1. **Guarda anti-v0.1.0 (Task 2):** com `--vcs-ref=HEAD` temporariamente removido de `copiar()`, `bash .template-tests/test_copier_copy.sh` saiu com código 1 e a mensagem `FALHOU: árvore gerada não tem o logo da Fase 6: a suíte está renderizando uma tag antiga, não o HEAD`. Flag restaurada em seguida; `bash .template-tests/test_copier_copy.sh` voltou a sair com código 0.
2. **Propagação de código de saída (Task 3):** `bash .template-tests/ensaio_django.sh testar core.tests.nao_existe` saiu com código 1 (`ModuleNotFoundError`), confirmando que o código de saída real do Django é propagado, não mascarado.
3. **Frescor do fingerprint em cinco passos (Task 3), todos confirmados:**
   1. Acrescentada uma linha de comentário em `core/views.py` → `testar core.tests.test_pwa` **recriou** o banco (mensagem `ENSAIO: recriando banco de ensaio...` em stderr).
   2. Linha removida.
   3. `testar` novamente → **recriou** outra vez (conteúdo mudou de novo, mesmo voltando ao estado original — cada edição é uma mudança de conteúdo distinta na sequência temporal).
   4. `touch core/views.py` sem alterar nenhum byte → `testar` **reaproveitou** o banco (3.5s, sem mensagem de recriação) — prova de que o fingerprint é de conteúdo, não de `mtime`.
4. **Caminho ausente (Task 3):** `rm core/README.md` (sem `git rm`) seguido de `testar core.tests.test_pwa` **recriou** o banco sem erro de script (o caminho entrou no hash como `AUSENTE`); arquivo restaurado com `git checkout --` em seguida.
5. **Verificação final ponta a ponta:** após `derrubar` (confirmado: `docker compose ls` não lista mais o projeto, diretório da cópia removido), o comando de verificação do plano — `bash -n .template-tests/ensaio_django.sh && bash .template-tests/ensaio_django.sh testar core apps.exemplo` — rodou do zero (criação completa) e terminou com sucesso, 77 testes.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Os planos 07-03 a 07-07 já têm `.template-tests/ensaio_django.sh` disponível como comando único para rodar qualquer alvo Django dentro de uma cópia real gerada do working tree.
- Toda a regressão de `.template-tests/` (matriz Copier copy, suíte `test_04_*`, banco de ensaio) está verde.
- O README do template ainda não lista `ensaio_django.sh` no inventário de suítes — isso é responsabilidade do plano 07-08, por decisão explícita do próprio plano 07-01 (não antecipar o fechamento do inventário).

---
*Phase: 07-herdar-o-design-system-do-pca*
*Completed: 2026-08-23*

## Self-Check: PASSED

All created/modified files verified present on disk; all task and metadata commit hashes (b336a7d, c52ed5d, 9942543, a418568) verified present in git log.
