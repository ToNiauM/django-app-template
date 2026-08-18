---
phase: 04-templatiza-o-copier
plan: 05
subsystem: infra
tags: [copier, docker-compose, postgresql, rclone, backup, retention]

requires:
  - phase: 04-templatiza-o-copier
    provides: "Template Copier in-place com identidade parametrizada e app exemplo opcional."
provides:
  - "Compose renderizado com nome igual ao slug, volume pgdata gerenciado e publicação web limitada a loopback."
  - "Serviço backup containerizado com PostgreSQL 17, rclone 1.68.2 verificado, agenda validada e dcron em foreground."
  - "Dump custom diário/semanal e retenção compartilhada por modtime com ensaio remoto confinado."
affects: [04-06, 04-07, template-copier, operations]

actuals:
  tokens: 4792
  tasks: 2
  commits: 5

tech-stack:
  added: [rclone-1.68.2-in-container, dcron]
  patterns:
    - "Recursos Compose são isolados pelo nome gerado a partir do slug."
    - "Valores de agenda entram no crontab somente depois de validação restritiva no entrypoint."
    - "Retenção por modtime é implementada uma vez e reutilizada pelo backup e pelo ensaio."

key-files:
  created:
    - compose.yml.jinja
    - ops/backup/Dockerfile
    - ops/backup/entrypoint.sh
    - ops/backup/backup.sh
    - ops/backup/retencao.sh
    - ops/backup/testar_retencao.sh
    - .template-tests/test_04_05_backup.py
  modified:
    - .env.example.jinja
  removed:
    - compose.yml

key-decisions:
  - "O nome de projeto Compose é renderizado pelo sistema_slug, mantendo pgdata gerenciado e independente do diretório destino."
  - "A agenda é validada em shell antes de gravar /etc/crontabs/root para impedir valores de .env virarem sintaxe de cron."
  - "O backup usa pg_dump customizado e retenção única ordenada pelo modtime do R2."

patterns-established:
  - "Operação recebe banco, R2, agenda e retenção exclusivamente por .env; nenhum segredo participa das respostas Copier."
  - "Ensaios que removem objetos remotos usam namespace descartável slug+PID, bloqueio de daily/weekly e trap de limpeza."

requirements-completed: [TPL-02, TPL-04, INF-03, INF-04]

coverage:
  - id: D1
    description: "Stack Copier renderizada isola recursos pelo slug, conserva loopback e mantém backup sem portas públicas."
    requirement: INF-04
    verification:
      - kind: integration
        ref: ".template-tests/test_04_05_backup.py#test_rendered_compose_is_isolated_and_backup_is_internal"
        status: pass
      - kind: other
        ref: "docker compose config --format json no destino Copier Aurora"
        status: pass
    human_judgment: false
  - id: D2
    description: "Imagem e entrypoint de backup validam configuração antes do dcron e preservam segredos como placeholders."
    requirement: INF-03
    verification:
      - kind: integration
        ref: ".template-tests/test_04_05_backup.py#test_backup_image_and_entrypoint_validate_the_operational_boundary"
        status: pass
      - kind: other
        ref: "docker build ./ops/backup e docker run com BACKUP_HORA=24"
        status: pass
    human_judgment: false
  - id: D3
    description: "Dump customizado, cópias diária/semanal e retenção por modtime têm scripts POSIX e ensaio remoto confinado."
    requirement: INF-03
    verification:
      - kind: integration
        ref: ".template-tests/test_04_05_backup.py#test_dump_retention_and_operational_test_are_confined"
        status: pass
      - kind: other
        ref: "sh -n ops/backup/backup.sh ops/backup/retencao.sh ops/backup/testar_retencao.sh"
        status: pass
    human_judgment: false

duration: 10min
completed: 2026-08-18
status: complete
---

# Phase 04 Plan 05: Compose e Backup Containerizado Summary

**Stack Copier isolada pelo slug com backup PostgreSQL customizado, rclone verificado e retenção diária/semanal configurada via `.env`.**

## Performance

- **Duration:** 10 min
- **Started:** 2026-08-18T16:49:00Z
- **Completed:** 2026-08-18T16:58:51Z
- **Tasks:** 2/2
- **Files modified:** 9

## Accomplishments

- Migrou a definição Compose para `compose.yml.jinja`, fixa `name: {{ sistema_slug }}` e preserva `pgdata` gerenciado e o bind web `127.0.0.1`.
- Adicionou serviço de backup interno, dependente do healthcheck do banco, com `init: true`, imagem PostgreSQL 17 e rclone 1.68.2 baixado com checksum.
- Implementou validação de hora, minuto, retenções e dia semanal antes de escrever o crontab, dump `pg_dump --format=custom`, cópia daily/weekly e retenção compartilhada por modtime.

## Task Commits

1. **Task 1: Renderizar Compose isolado e imagem agendada de backup**
   - `3182864` — `test(04-05): add failing backup stack integration`
   - `fa75559` — `feat(04-05): add isolated scheduled backup stack`
2. **Task 2: Implementar dump diário/semanal e retenção verificável**
   - `a4188f7` — `test(04-05): specify backup retention scripts`
   - `d491d18` — `feat(04-05): implement containerized backup retention`

## Files Created/Modified

- `compose.yml.jinja` — stack nomeada pelo slug, web em loopback e serviço backup sem porta publicada.
- `.env.example.jinja` — placeholders R2 e defaults de agenda/retenção seguros.
- `ops/backup/Dockerfile` e `entrypoint.sh` — imagem com checksum e inicialização validada do dcron.
- `ops/backup/{backup,retencao,testar_retencao}.sh` — ciclo de dump, retenção por modtime e ensaio remoto isolado.
- `.template-tests/test_04_05_backup.py` — cobertura TDD de renderização Copier, segredos, validação e scripts.

## Decisions Made

- `pgdata` segue gerenciado pelo Compose: a identidade de `name: {{ sistema_slug }}` fornece isolamento sem pré-criação de host.
- Os valores de cron são enumerados e/ou numéricos antes da escrita de `/etc/crontabs/root`, impedindo injeção de configuração pelo `.env`.
- O ensaio não recebe um prefixo de produção: cria namespace com `SISTEMA_SLUG` e PID, recusa `daily`/`weekly` e limpa por trap.

## Verification

- `python .template-tests/test_04_03_identity.py` — 3 testes passaram.
- `python .template-tests/test_04_04_optional_exemplo.py` — 3 testes passaram.
- `python .template-tests/test_04_05_backup.py` — 4 testes passaram.
- `docker build --tag sistema-base-04-05-backup:verification ./ops/backup` — passou; checksum confirmou `rclone-v1.68.2-linux-amd64.zip`.
- `docker run` com `BACKUP_HORA=24` — rejeitado pelo entrypoint antes de iniciar o dcron.
- Cópia real Copier Aurora, `docker compose config`, sintaxe de todos os scripts renderizados e varredura de identidade PCA/sistema_base — passaram.

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None.

## Next Phase Readiness

O template renderiza uma stack operacional autocontida e está pronto para o ensaio de restore, vhost Nginx e runbook dos planos 04-06/04-07. Credenciais R2 reais continuam deliberadamente fora do template.

## Self-Check: PASSED

- Todos os oito artefatos operacionais e o teste TDD existem no repositório.
- Os quatro commits TDD/implementação listados acima existem no histórico.
- `IDEIA.md` permaneceu não rastreado e inalterado.

---
*Phase: 04-templatiza-o-copier*
*Completed: 2026-08-18*
