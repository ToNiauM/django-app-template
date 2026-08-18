---
phase: 05-verifica-o-e-documenta-o
plan: 01
subsystem: testing
tags: [copier, docker-compose, django, tracer, e2e]
requires:
  - phase: 04-templatiza-o-copier
    provides: "template Copier, matriz de copy/update e stack Docker renderizada"
provides:
  - "Tracer isolado Copier → Compose → Django → HTTP para uma cópia gerada"
  - "Ambiente de build collectstatic completo e não secreto"
  - "Pacote raiz apps importável em todas as variantes renderizadas"
affects: [05-02, 05-03, qa-01, qa-02]
actuals:
  tokens: 2703
  tasks: 1
  commits: 3
tech-stack:
  added: []
  patterns: ["tracer POSIX com recursos Compose confinados", "settings de build não secretas", "validação Django dentro da cópia Copier"]
key-files:
  created:
    - .template-tests/test_05_nascimento.sh
    - .template-tests/test_04_07_collectstatic.py
    - apps/__init__.py
  modified:
    - Dockerfile
    - .template-tests/test_04_04_optional_exemplo.py
key-decisions:
  - "O collectstatic recebe apenas valores fictícios não secretos no build; o .env continua prevalecendo em runtime."
  - "O preflight usa o contrato focado de collectstatic; a matriz Copier completa roda separadamente porque leva mais que 45 segundos."
patterns-established:
  - "O nascimento de template deve ser validado contra uma cópia Copier descartável, nunca a raiz Jinja."
requirements-completed: [QA-01, QA-02]
coverage:
  - id: D1
    description: "Cópia Copier com app exemplo sobe, migra, cria superusuário e executa a suíte Django."
    requirement: QA-01
    verification:
      - kind: integration
        ref: .template-tests/test_05_nascimento.sh
        status: pass
    human_judgment: false
  - id: D2
    description: "Tracer confina Compose em loopback, prova /healthz e /login/, e remove somente recursos próprios."
    requirement: QA-02
    verification:
      - kind: integration
        ref: .template-tests/test_05_nascimento.sh --keep
        status: pass
    human_judgment: false
duration: 3h 16min
completed: 2026-08-18
status: complete
---

# Phase 05 Plan 01: Provar o Nascimento Completo Summary

**Tracer POSIX agora prova uma cópia Copier real do build Docker até os 69 testes Django, superusuário e smokes HTTP em loopback.**

## Performance

- **Duration:** 3h 16min
- **Started:** 2026-08-18T16:16:44-03:00
- **Completed:** 2026-08-18T19:32:43Z
- **Tasks:** 1
- **Files modified:** 5

## Accomplishments

- Criou o tracer efêmero com preflight, respostas Copier determinísticas, segredos temporários, Compose isolado, migração, superusuário e verificação HTTP.
- Corrigiu o ambiente de `collectstatic` para incluir toda a identidade obrigatória sem inserir segredos, domínios ou credenciais na imagem.
- Corrigiu a descoberta Django de `apps.exemplo` no sistema gerado e provou os modos padrão e `--keep`.

## Task Commits

1. **Task 1: Provar o nascimento completo em uma cópia Copier efêmera**
   - `fa980f7` `fix(05-01): supply build-safe Django identity for collectstatic`
   - `f9a533b` `fix(05-01): make generated apps importable for Django tests`
   - `fd1425e` `test(05-01): prove rendered Copier system birth`

## Files Created/Modified

- `Dockerfile` — fornece identidade fictícia necessária ao `collectstatic` no estágio de build.
- `.template-tests/test_04_07_collectstatic.py` — fixa o contrato de todas as settings obrigatórias no build.
- `apps/__init__.py` — torna os apps gerados um pacote Python descobrível pelo runner Django.
- `.template-tests/test_04_04_optional_exemplo.py` — confirma o pacote raiz nas duas variantes Copier.
- `.template-tests/test_05_nascimento.sh` — ensaio completo e autocontido de nascimento, inclusive retenção segura em `--keep`.

## Decisions Made

- Valores de build são deliberadamente não secretos e são substituídos pelo `.env` da cópia em runtime.
- O preflight permanece rápido usando o contrato do build; os 13 testes de contrato Copier seguem obrigatórios na regressão integral, executada separadamente.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `collectstatic` não recebia a identidade exigida pelos settings.**
- **Found during:** Task 1
- **Issue:** O Dockerfile passava `SECRET_KEY` e `DATABASE_URL`, mas omitira `SISTEMA_NOME`, `SISTEMA_SIGLA` e `COR_PRIMARIA`.
- **Fix:** Adicionados valores fictícios não secretos no estágio de build e um teste de contrato focado.
- **Files modified:** `Dockerfile`, `.template-tests/test_04_07_collectstatic.py`
- **Verification:** Build da cópia renderizada completou `collectstatic` e o tracer passou.
- **Committed in:** `fa980f7`

**2. [Rule 1 - Bug] O runner Django não descobria `apps.exemplo` na cópia.**
- **Found during:** Task 1
- **Issue:** A ausência de `apps/__init__.py` deixava o namespace sem `__file__` para a descoberta do `manage.py test`.
- **Fix:** Criado pacote raiz `apps` e assertions de renderização nas variantes com e sem exemplo.
- **Files modified:** `apps/__init__.py`, `.template-tests/test_04_04_optional_exemplo.py`
- **Verification:** A cópia executou 69 testes de `core` e `apps.exemplo` com sucesso.
- **Committed in:** `f9a533b`

**3. [Rule 3 - Blocking] O preflight não cabia no limite de 45 segundos ao rodar a matriz inteira.**
- **Found during:** Task 1
- **Issue:** Os 13 contratos `test_04_*.py` levam 79.9 segundos por realizarem múltiplas cópias Copier reais.
- **Fix:** O preflight executa o contrato focado de `collectstatic`; a matriz completa continuou sendo executada separadamente e passou.
- **Files modified:** `.template-tests/test_05_nascimento.sh`
- **Verification:** Preflight passou, a matriz integral passou em 79.9 s e os ensaios Copier copy/update passaram.
- **Committed in:** `fd1425e`

---

**Total deviations:** 3 auto-fixed (2 Rule 1, 1 Rule 3).
**Impact on plan:** Correções mínimas e causais; a evidência de QA-01/QA-02 foi fortalecida sem introduzir segredo ou recurso externo.

## Verification

- `python3 -m unittest discover -s .template-tests -p 'test_04_*.py'` — 13 testes passaram em 79.908 s.
- `.template-tests/test_copier_copy.sh` — passou.
- `.template-tests/test_copier_update.sh` — passou.
- `.template-tests/test_05_nascimento.sh` — passou: 69 testes Django, superusuário, `/healthz` e `/login/`.
- `.template-tests/test_05_nascimento.sh --keep` — passou e expôs somente `NASCIMENTO_DESTINO`, `NASCIMENTO_PROJETO_COMPOSE` e `NASCIMENTO_URL`; os recursos retidos foram removidos manualmente após a confirmação.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- O modo `--keep` oferece o destino, projeto Compose e URL não sensíveis para a inspeção visual do Plano 05-03.
- A divergência de tempo do preflight está registrada em `.planning/WINDOWS.md`; o contrato completo continua coberto pela regressão integral.

## Self-Check: PASSED

- Encontrados: `.template-tests/test_05_nascimento.sh`, `.template-tests/test_04_07_collectstatic.py` e `apps/__init__.py`.
- Encontrados: `fa980f7`, `f9a533b` e `fd1425e` no histórico Git.

---
*Phase: 05-verifica-o-e-documenta-o*
*Completed: 2026-08-18*
