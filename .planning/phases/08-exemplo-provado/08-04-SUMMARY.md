---
phase: 08-exemplo-provado
plan: 04
subsystem: testing
tags: [prv-01, copier, docker-compose, unittest, smoke-http, csrf, drift-sha256]
requires:
  - "08-01: fixture apps/diarias (modelo, migração 0001, views, seed)"
  - "08-02: fixture apps/diarias (templates, dashboard, testes internos)"
  - "08-03: teste negativo de vazamento (garante que a instalação fica restrita à cópia)"
provides:
  - "Prova de ponta a ponta do PRV-01: fixture instala numa cópia Copier real (banco de ensaio), migração aplica, testes do app passam no container e smoke HTTP responde 302 anônimo / 200 autenticado com CSRF real"
  - "Constantes de patch nomeadas (LINHA_SETTINGS, LINHA_URLS, LINHAS_NAV) — o texto exato que o guia da Fase 9 mandará o leitor digitar"
  - "Instalação idempotente com detecção de drift por sha256 e migrate diarias zero antes de trocar models/migrations"
  - "Correção do template: dados/ excluído do contexto de build Docker (rebuild pós-boot funcionava zero vezes)"
affects:
  - "09 (escrita do guia): cita LINHA_SETTINGS/LINHA_URLS/LINHAS_NAV como os passos do leitor; o rebuild que o guia ensina depende do conserto do .dockerignore"
tech-stack:
  added: []
  patterns:
    - "Captura única do banco de ensaio (subir uma vez em setUpClass) + laço próprio de /healthz 180x1s após up -d --build (Pitfall 2)"
    - "Drift por sha256 (caminho relativo + conteúdo, padrão impressao_subarvore) fixture x instalado a cada execução (Pitfalls 4-5)"
    - "Jar de cookies que descarta Secure só no cliente de teste — postura de produção da cópia intocada"
key-files:
  created:
    - .template-tests/test_08_guia_prova.py
  modified:
    - .dockerignore
key-decisions:
  - "dados/ entra no .dockerignore do template: o bind mount ./dados/pg (uid 999) quebrava todo docker compose up -d --build após o primeiro boot com permission denied no sender do BuildKit — exatamente o passo que o README e o guia ensinam; excluir também impede assar dados do PostgreSQL na imagem"
  - "_JarraSemSecure descarta o atributo Secure dos cookies APENAS no cliente de smoke: CSRF_COOKIE_SECURE/SESSION_COOKIE_SECURE=True (incondicionais, postura de produção) impedem jar padrão de reenviar cookies sobre HTTP puro em 127.0.0.1; nenhuma proteção do servidor foi tocada e a validação real do token é exercitada"
  - "Banco de ensaio fica COM o fixture instalado ao final (Pattern 4) — registrado na docstring como convenção: nenhuma suíte futura deve assumir banco puro"
  - "Usuário de smoke por shell -c get_or_create + set_password com secrets.token_urlsafe a cada execução (alternativa robusta da Assumption A3) — nada de createsuperuser --noinput, cuja mensagem de duplicata varia com a versão"
patterns-established:
  - "Instalação de app na cópia = os passos do leitor: copytree + 3 patches idempotentes com guarda 'not in texto' + up -d --build web"
  - "migrate diarias zero com o código ANTIGO ainda instalado antes de sobrescrever models/migrations em drift (Pitfall 5)"
requirements-completed: [PRV-01]
metrics:
  duration: 14min
  completed: 2026-08-26
---

# Phase 08 Plan 04: Prova de ponta a ponta do guia Summary

**PRV-01 verde de ponta a ponta: `test_08_guia_prova.py` instala o fixture na cópia Copier real pelos passos do leitor, prova migração + `makemigrations --check` + testes do app dentro do container e smoke HTTP 302/200 com dança real de CSRF — suíte integral do projeto com 48 testes OK (39 anteriores + 3 vazamento + 6 prova).**

## Performance

- **Duration:** 14min (mais criação/recriação do banco de ensaio em background)
- **Started:** 2026-08-26T12:29:34Z
- **Completed:** 2026-08-26T12:43:30Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- **Núcleo da suíte (setUpClass único):** `subir` invocado UMA vez (única chamada ao harness em toda a suíte); parse de `ENSAIO_DESTINO/PROJETO/PORTA/URL`; drift por sha256 fixture×instalado com três estados (ausente/idêntico/divergente) e `migrate diarias zero` antes de sobrescrever quando o drift toca `models.py`/`migrations/`; instalação pelos passos do leitor (copytree sem `__pycache__` + patches idempotentes nas 3 âncoras); rebuild só quando algo mudou, seguido de laço próprio de `/healthz` (180×1s).
- **Provas in-container (4 métodos):** `migrate --noinput` código 0; `showmigrations diarias` com `[X] 0001_initial`; `makemigrations diarias --check --dry-run` limpo (migração escrita à mão consistente com models.py); `manage.py test apps.diarias --noinput` verde (12 testes do fixture dentro do container).
- **Smoke HTTP (2 métodos):** 302 → `/login/` nas 3 telas para anônimo (redirect desabilitado); usuário de smoke idempotente com senha efêmera; login em tentativa única com cookie jar + `csrfmiddlewaretoken` + `Referer`; 200 autenticado com H1 "Diárias e passagens", `href="/diarias/dashboard/"` dentro do recorte do `<nav>` da listagem e `id="paleta-graficos"` no dashboard. Sem seed — telas respondem 200 com banco vazio.
- **Idempotência provada:** duas execuções consecutivas verdes; a segunda pela via barata (19s, zero ocorrência de build na saída).
- **Suíte integral:** `python3 -m unittest discover -s .template-tests -p 'test_*.py'` → 48 testes OK em 186s; nenhum teste do fixture coletado no host (fixtures/ sem `__init__.py`).

## Task Commits

Each task was committed atomically:

1. **Task 1: Núcleo da suíte — subir, drift, rebuild, migrar, testar in-container** - `3f087af` (test)
2. **Task 2: Smoke HTTP — 302 anônimo e 200 autenticado com CSRF real** - `7342902` (test)
3. **Task 3: Execução de ponta a ponta e suíte integral** - `c9cef98` (fix, deviation) + `28131fc` (test)

## Files Created/Modified

- `.template-tests/test_08_guia_prova.py` - Suíte de prova de ponta a ponta do PRV-01 (579 linhas, unittest stdlib): setUpClass caro único, 6 métodos ordem-independentes, constantes de patch nomeadas para a Fase 9
- `.dockerignore` - `dados/` excluído do contexto de build (conserto de template — ver Deviations)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Rebuild pós-boot quebrado: `dados/` fora do `.dockerignore`**
- **Found during:** Task 3 (primeiro `up -d --build web` da suíte)
- **Issue:** o bind mount `./dados/pg` da Fase 6 é gravado pelo initdb como uid 999; o sender do BuildKit falha com `permission denied` ao transferir o contexto — TODO `docker compose up -d --build` após o primeiro boot falhava em qualquer sistema gerado (o build inicial passa só porque `dados/` ainda não existe). É exatamente o passo que o README e o guia da Fase 9 ensinam para instalar código novo.
- **Fix:** linha `dados/` acrescentada ao `.dockerignore` do template (chega verbatim a toda cópia). Efeito colateral desejado: o diretório de dados do PostgreSQL nunca pode ser assado na imagem, mesmo onde for legível.
- **Files modified:** `.dockerignore`
- **Commit:** `c9cef98`
- **Consequência operacional:** a mudança invalidou a impressão digital do banco de ensaio — recriação completa disparada em background (contrato do harness) antes da execução verde.

**2. [Rule 1 - Bug, escopo da própria suíte] Cookies `Secure` sobre HTTP puro no smoke**
- **Found during:** Task 3 (POST de login retornava 403)
- **Issue:** a cópia mantém `CSRF_COOKIE_SECURE = True` e `SESSION_COOKIE_SECURE = True` incondicionais (postura de produção); o cookie jar padrão honra o atributo e jamais reenviaria `csrftoken`/`sessionid` para `http://127.0.0.1` — o 403 vinha do cookie ausente, não do token.
- **Fix:** `_JarraSemSecure` (CookieJar que zera `cookie.secure` ao armazenar) usada só no cliente de smoke. Nenhuma configuração do servidor tocada (T-08-P4-03 preservada: a dança de CSRF real continua sendo validada pelo Django).
- **Files modified:** `.template-tests/test_08_guia_prova.py`
- **Commit:** `28131fc`

## Verification Evidence

- `test_08_guia_prova.py`: 6/6 OK duas vezes seguidas; segunda execução em 19s sem rebuild (via barata do drift)
- In-container: `showmigrations diarias` → ` [X] 0001_initial`; `manage.py test apps.diarias --noinput` código 0; `makemigrations diarias --check --dry-run` código 0
- test_command integral: `Ran 48 tests ... OK` (9 módulos anteriores = 39 testes; +3 vazamento; +6 prova); os 4 `test_*.sh` são tracers à parte, fora do discover
- Threat register: T-08-P4-01 (senha efêmera via secrets, só memória), T-08-P4-02 (tentativa única de login), T-08-P4-03 (CSRF real, nada desligado no servidor), T-08-P4-04 (escrita restrita a ENSAIO_DESTINO), T-08-P4-05 (drift sha256 + migrate zero) — todas as mitigações implementadas

## Known Stubs

Nenhum — a suíte exercita código real de ponta a ponta; nenhum placeholder ou dado fixo mascarando funcionalidade.

## Next Phase Readiness

- Fase 9 pode citar `LINHA_SETTINGS`, `LINHA_URLS` e `LINHAS_NAV` de `test_08_guia_prova.py` como as edições literais do leitor
- Banco de ensaio fica com `apps/diarias` instalado (estado correto por convenção registrada na docstring) — suítes futuras que precisem de cópia pura usam render leve próprio
- Critérios 1 e 3 do roadmap da fase verdes; PRV-01 completo

## Self-Check: PASSED

- test_08_guia_prova.py existe; commits 3f087af, 7342902, c9cef98, 28131fc presentes no log; nenhuma deleção de arquivo rastreado nos 4 commits
