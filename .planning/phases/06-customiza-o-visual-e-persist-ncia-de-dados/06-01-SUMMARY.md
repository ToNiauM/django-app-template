---
phase: 06-customiza-o-visual-e-persist-ncia-de-dados
plan: 01
subsystem: infra
tags: [docker-compose, postgres, bind-mount, copier, gitignore, unittest]

# Dependency graph
requires:
  - phase: 04 (Copier e operação)
    provides: compose.yml.jinja com serviços db/web/backup, rede de testes .template-tests e tracer de nascimento
provides:
  - Serviço db com bind mount configurável ${PGDATA_DIR:-./dados/pg} — `docker compose down -v` não destrói mais o banco (D-73)
  - Sistema gerado nasce com .gitignore protegendo .env e /dados/ via .gitignore.jinja (D-74, Pitfall 3)
  - PGDATA_DIR documentado no .env.example.jinja (prefixo ./ obrigatório, sempre subdiretório)
  - test_06_persistencia.py: contrato dos fontes + prova por cópia real (Assumption A4)
  - Tracer de nascimento prova sobrevivência a down -v e limpa dados uid 999 via container root
affects: [06-02, 06-03, backup, operacao]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Bind mount com default no compose (${VAR:-./caminho}) em vez de named volume para dados que não podem morrer com down -v"
    - "Arquivo .jinja sem variáveis usado só para renderizar por cima de arquivo verbatim excluído do _exclude (precedente README.md.jinja)"
    - "copier copy --vcs-ref=HEAD em toda a rede de testes do template — com tag de release no repo, o default do Copier é a última tag"

key-files:
  created:
    - .gitignore.jinja
    - .template-tests/test_06_persistencia.py
  modified:
    - compose.yml.jinja
    - .env.example.jinja
    - copier.yml
    - .gitignore
    - .template-tests/test_04_05_backup.py
    - .template-tests/test_05_nascimento.sh

key-decisions:
  - "Bind mount ${PGDATA_DIR:-./dados/pg} substitui o named volume pgdata — down -v remove só named volumes; bind mount sobrevive por construção (D-73/D-76)"
  - ".gitignore saiu do _exclude do copier.yml para o .gitignore.jinja renderizar no destino — mesmo mecanismo do README.md.jinja (Pitfall 3)"
  - "Testes e tracer do template usam copier copy --vcs-ref=HEAD: desde a tag v0.1.0 o Copier copiava a tag, não o estado atual (Rule 3)"

patterns-established:
  - "Persistência por construção: dados críticos em bind mount visível no host, nunca em volume gerenciado pelo Compose"
  - "Limpeza de artefatos uid 999 em /tmp via docker run --rm -v ... postgres:17 rm -rf"

requirements-completed: [C4]

# Metrics
duration: 8min
completed: 2026-08-19
---

# Phase 06 Plan 01: Persistência de Dados por Bind Mount Summary

**PostgreSQL do sistema gerado agora vive em bind mount ./dados/pg (configurável via PGDATA_DIR) — `down -v` provadamente não perde dados — e todo sistema nasce com .gitignore protegendo .env e /dados/.**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-08-19T08:30:21Z
- **Completed:** 2026-08-19T08:38:30Z
- **Tasks:** 3/3
- **Files modified:** 8

## Accomplishments

- Critério 4 do roadmap provado por teste real: o tracer cria superusuário, roda `docker compose down --volumes`, sobe de novo e reencontra o usuário — o bind mount torna a operação historicamente destrutiva inofensiva por construção
- Sistema gerado deixa de nascer sem `.gitignore`: `.gitignore.jinja` renderiza `.env`, `/dados/` e demais entradas no destino (`git add .` nunca commita segredos nem o banco)
- Rede de testes atualizada: `test_04_05` valida o novo contrato de bind mount no JSON de `docker compose config`; `test_06_persistencia.py` (6 testes) cobre fontes e cópia real
- Tracer se limpa por completo mesmo com `dados/pg` uid 999 (remoção via container root `postgres:17`)

## Task Commits

Each task was committed atomically:

1. **Task 1: Bind mount no compose, PGDATA_DIR no .env.example e .gitignore do sistema gerado** - `f5efcf0` (feat)
2. **Task 2: Rede de testes — atualizar test_04_05 e criar test_06_persistencia** - `a22480d` (test)
3. **Task 3: Tracer de nascimento — limpeza uid 999 e prova de sobrevivência a down -v** - `06373ce` (test)

## Files Created/Modified

- `compose.yml.jinja` - db usa `${PGDATA_DIR:-./dados/pg}:/var/lib/postgresql/data`; bloco `volumes:` de topo removido; web/backup/healthcheck intactos
- `.env.example.jinja` - bloco pt-BR documentando PGDATA_DIR (prefixo `./` obrigatório, sempre subdiretório) com default comentado
- `copier.yml` - `.gitignore` removido do `_exclude` com comentário explicando o mecanismo de substituição
- `.gitignore` - template também ignora `/dados/`
- `.gitignore.jinja` - fonte do `.gitignore` do sistema gerado (sem `.venv-template/`, com `/dados/`)
- `.template-tests/test_04_05_backup.py` - contrato do bind mount no compose config resolvido
- `.template-tests/test_06_persistencia.py` - contrato dos fontes + prova de cópia real (A4)
- `.template-tests/test_05_nascimento.sh` - prova de down -v antes de SUCESSO=true; limpeza uid 999 em limpar()

## Decisions Made

- Bind mount com default relativo no próprio compose (não no .env) — sistema gerado sobe sem configurar nada e os dados ficam visíveis em `./dados/pg`
- `--vcs-ref=HEAD` nos `copier copy` da rede de testes: desde a criação da tag `v0.1.0` o Copier copiava a tag por padrão, não a árvore de trabalho — sem isso os testes novos validariam conteúdo congelado

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Copier pinado na tag v0.1.0 em vez do estado atual do template**
- **Found during:** Task 2 (o teste de cópia real falhou: destino sem `.gitignore` e compose ainda com `pgdata`)
- **Issue:** com a tag de release `v0.1.0` criada em 2026-08-18, `copier copy` de um repositório git passa a copiar a última tag por padrão — os renders dos testes e do tracer validavam o template congelado na tag, não os fontes atuais
- **Fix:** `--vcs-ref=HEAD` adicionado aos `copier copy` de `test_06_persistencia.py`, `test_04_05_backup.py` e `test_05_nascimento.sh` (arquivos do escopo do plano), com comentário pt-BR
- **Files modified:** .template-tests/test_06_persistencia.py, .template-tests/test_04_05_backup.py, .template-tests/test_05_nascimento.sh
- **Commits:** a22480d, 06373ce
- **Out of scope:** `test_04_03_identity.py`, `test_copier_copy.sh`, `test_04_06_operations.py`, `test_04_04_optional_exemplo.py` também rendem da tag (passam hoje, mas validam conteúdo antigo) — registrados em `deferred-items.md` da fase

## Verification

- `python3 -m unittest discover -s .template-tests -p 'test_06_persistencia.py'` → OK (6 testes)
- `python3 -m unittest discover -s .template-tests -p 'test_04_05_backup.py'` → OK (4 testes)
- `.template-tests/test_05_nascimento.sh` → `OK: dados sobreviveram a down --volumes + up -d` e `OK: nascimento completo da cópia Copier passou.`
- `/tmp` limpo após o tracer (`ls -d /tmp/tmp*/nascimento` vazio); nenhum container remanescente
- `git diff` de compose.yml.jinja restrito ao serviço db e à remoção do bloco de topo

## Known Stubs

Nenhum — nenhum placeholder ou dado vazio hardcoded foi introduzido.

## Threat Flags

Nenhuma superfície nova fora do threat model do plano: T-06-01 e T-06-02 mitigados conforme o registro (`/dados/` e `.env` no `.gitignore.jinja`); T-06-03/T-06-04 aceitos conforme disposição.

## Self-Check: PASSED

Arquivos criados e commits f5efcf0/a22480d/06373ce verificados no repositório.

## Next Phase Readiness

- Plano 06-02 (customização visual) independente deste — pronto para executar
- Plano 06-03 pode referenciar o troubleshooting de permissões do diretório de dados (T-06-04)
