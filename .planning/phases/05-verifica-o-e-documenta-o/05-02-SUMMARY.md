---
phase: 05-verifica-o-e-documenta-o
plan: 02
subsystem: documentation
tags: [readme, runbook, copier, nginx, tls, dns]
requires:
  - phase: 05-verifica-o-e-documenta-o
    provides: "tracer de nascimento .template-tests/test_05_nascimento.sh aprovado na Wave 1 (05-01)"
  - phase: 04-templatiza-o-copier
    provides: "copier.yml, .env.example.jinja, compose.yml.jinja, vhost Nginx gerado e ops/MIGRACAO.md.jinja"
provides:
  - "README-raiz como runbook canônico do template, do copier copy ao proxy/TLS/DNS"
  - "Seção de regressão que distingue contratos da fonte, ensaio real de nascimento e inspeção manual"
affects: [05-03, doc-01]
actuals:
  tokens: 2100
  tasks: 2
  commits: 2
tech-stack:
  added: []
  patterns: ["runbook linear numerado sincronizado com o tracer executável", "documentação em camadas com handoff explícito aos documentos renderizados"]
key-files:
  created: []
  modified:
    - README.md
key-decisions:
  - "A regressão foi consolidada em uma única seção após a publicação; a seção de releases passou a referenciá-la em vez de duplicar comandos."
  - "As credenciais R2 ficam explícitas como dispensáveis na prova inicial local, pertencendo ao serviço backup."
patterns-established:
  - "Comandos de runtime do README-raiz só existem após a entrada no diretório gerado; a raiz Jinja permanece não executável."
requirements-completed: [DOC-01]
coverage:
  - id: D1
    description: "Operador percorre no README-raiz a jornada completa do copier copy ao login/shell/CRUD/dashboard sem executar Django/Compose na árvore Jinja."
    requirement: DOC-01
    verification:
      - kind: contract
        ref: "python3 -c (ordem dos marcadores em '## Nascimento local de um sistema')"
        status: pass
    human_judgment: false
  - id: D2
    description: "Publicação documenta loopback, DNS, 80/443, Certbot, vhost gerado, nginx -t, HTTPS externo e link para ops/MIGRACAO.md; regressão lista os quatro comandos executáveis."
    requirement: DOC-01
    verification:
      - kind: contract
        ref: "python3 -c (conteúdo de '## Publicação com proxy, TLS e DNS')"
        status: pass
    human_judgment: false
duration: 19min
completed: 2026-08-18
status: complete
---

# Phase 05 Plan 02: README Canônico do Nascimento Summary

**README-raiz virou runbook operacional completo — nascimento local numerado, telas navegáveis, publicação proxy/TLS/DNS e regressão em três camadas sincronizada com o tracer aprovado.**

## Performance

- **Duration:** 19min
- **Started:** 2026-08-18T20:02:06Z
- **Completed:** 2026-08-18T20:21:00Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Criou `## Nascimento local de um sistema` como sequência numerada única: tag estável, `copier copy`, oito respostas, `.env` com segredos locais, primeiro commit com `.copier-answers.yml`, `config -q`, `up -d --build db web`, logs, `migrate --noinput` (`exec -T`), `createsuperuser` interativo e `curl` em `/healthz` — na mesma ordem dos marcos do tracer.
- Documentou as URLs concretas `/login/`, `/`, `/exemplo/` e `/exemplo/dashboard/` associadas a login, shell, CRUD e dashboard, sem inventar telas.
- Criou `## Publicação com proxy, TLS e DNS`: loopback invariante (`WEB_BIND_ADDRESS=127.0.0.1`), registro DNS, somente portas 80/443, Certbot, vhost gerado em `ops/nginx/<slug>.conf`, `sudo nginx -t`, restart e validação externa de `https://<hostname>/healthz`, com handoff a `ops/MIGRACAO.md` sem duplicar restore destrutivo.
- Consolidou `## Regressão do template` com os quatro comandos executáveis e descrição fiel do ensaio de nascimento; inspeção de navegador ficou qualificada como checkpoint manual complementar, sem alegar automação visual.

## Task Commits

1. **Task 1: Documentar o nascimento local até as telas navegáveis**
   - `0eeaa9a` `docs(05-02): documentar nascimento local completo no README-raiz`
2. **Task 2: Fechar proxy, TLS, DNS e regressão no runbook canônico**
   - `59fdd3c` `docs(05-02): fechar publicação proxy/TLS/DNS e regressão no README-raiz`

## Files Created/Modified

- `README.md` — runbook canônico do template: fronteira template-fonte, Copier 9.17.1 isolado, nascimento local numerado, telas navegáveis, convenção de portas, publicação proxy/TLS/DNS, regressão consolidada e releases/updates preservados.

## Decisions Made

- A seção de regressão saiu do topo e foi consolidada após a publicação, cobrindo contratos da fonte (`test_copier_copy.sh`, `test_copier_update.sh`, `test_04_*.py`) e ensaio real (`test_05_nascimento.sh`); a seção de releases agora referencia essa regressão em vez de duplicar o bloco de comandos.
- As credenciais R2 são documentadas como dispensáveis na prova inicial local (pertencem ao serviço `backup`), mantendo `db`/`web` como escopo do primeiro `up`, em espelho ao tracer.
- O link de migração aponta para `ops/MIGRACAO.md` renderizado no sistema gerado (fonte `ops/MIGRACAO.md.jinja`), preservando D-39/D-63 e evitando repetir comandos destrutivos de banco no roteiro de primeiro nascimento.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Worktree sem `.venv-template` para a verificação de regressão**
- **Found during:** Verificação geral do plano
- **Issue:** A `.venv-template/` é ignorada pelo Git e não existia no worktree; os scripts de regressão exigem o Copier aprovado em `ROOT/.venv-template`. Um symlink para a venv do checkout principal foi rejeitado pelo Copier (`ForbiddenPathError`).
- **Fix:** Cópia local (`cp -a`) da venv do checkout principal para o worktree — recurso efêmero, ignorado pelo Git, descartado com o worktree.
- **Files modified:** nenhum arquivo versionado.
- **Verification:** `copier --version` retornou `copier 9.17.1`; todos os ensaios de regressão passaram em seguida.
- **Committed in:** não aplicável (mudança apenas de ambiente).

---

**Total deviations:** 1 auto-fixed (Rule 3, ambiente do worktree).
**Impact on plan:** Nenhum impacto no conteúdo entregue; o diff versionado contém somente `README.md`.

## Verification

- Task 1 (ordem dos marcadores em `## Nascimento local de um sistema` + URLs `/login/`, `/exemplo/`, `/exemplo/dashboard/`) — PASS.
- Task 2 (conteúdo obrigatório de `## Publicação com proxy, TLS e DNS` + `\b80\b`/`\b443\b`) — PASS.
- `.template-tests/test_copier_copy.sh` — passou.
- `.template-tests/test_copier_update.sh` — passou (A→B→C com opt-out preservado).
- `python3 -m unittest discover -s .template-tests -p 'test_04_*.py'` — 13 testes passaram em 68.4 s.
- `.template-tests/test_05_nascimento.sh` — passou (exit 0): cópia descartável, Compose, migração, superusuário, 72 testes Django e smokes `/healthz`/`/login/`, com os mesmos marcos agora documentados.
- `git diff -- README.md` entre a base e HEAD mostra somente documentação; `README.md.jinja` e `ops/MIGRACAO.md.jinja` intocados.

## Known Stubs

None — o plano é somente documentação; nenhum stub de código foi criado.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- O Plano 05-03 pode usar o modo `--keep` do tracer (documentado na regressão) para a inspeção visual complementar das telas.
- DOC-01 marcado como completo em REQUIREMENTS.md; QA-01/QA-02 tiveram a tabela de rastreabilidade sincronizada com os checkboxes já concluídos pela Wave 1.

## Self-Check: PASSED

- Encontrado: `README.md` com as seções `## Nascimento local de um sistema`, `## Publicação com proxy, TLS e DNS` e `## Regressão do template`.
- Encontrados: `0eeaa9a` e `59fdd3c` no histórico Git.

---
*Phase: 05-verifica-o-e-documenta-o*
*Completed: 2026-08-18*
